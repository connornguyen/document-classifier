import io                                                        # lets us treat bytes in memory like a file — needed for PDF reading
import torch                                                    # PyTorch — runs the model
from fastapi import FastAPI, HTTPException, UploadFile, File    # FastAPI core + file upload tools
from fastapi.staticfiles import StaticFiles                     # serves static files (HTML, CSS, JS)
from fastapi.responses import FileResponse                      # sends a file as an HTTP response
from pydantic import BaseModel                                  # used to define request/response shapes
from transformers import AutoTokenizer, AutoModelForSequenceClassification  # loads DistilBERT + tokenizer
from pypdf import PdfReader                                     # extracts text from PDF files

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Document Classifier API",                            # shown in the Swagger UI at /docs
    description="Classifies business documents into Invoice, Contract, Report, or Email.",
    version="4.0.0"
)

DEFAULT_THRESHOLD = 0.6  # if confidence is below this, return "unknown" instead of guessing

app.mount("/static", StaticFiles(directory="app/static"), name="static")  # serve files from app/static/ at /static URL

# ── Load model once at startup ────────────────────────────────────────────────

MODEL_PATH  = "./models/distilbert-business"                    # folder where your saved model lives
LABEL_NAMES = ["Invoice", "Contract", "Report", "Email"]        # must match the order used during training
DEVICE      = torch.device("mps" if torch.backends.mps.is_available() else "cpu")  # use Apple GPU if available, else CPU

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)                           # loads the tokenizer (text → numbers)
    model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)      # loads the trained DistilBERT model
    model     = model.to(DEVICE)                                                    # moves model to GPU/CPU
    model.eval()                                                                    # switches to inference mode — disables dropout
    print(f"Model loaded on {DEVICE}")
except Exception as e:
    raise RuntimeError(                                         # if model files are missing, crash early with a clear message
        f"Could not load model from '{MODEL_PATH}'. "
        f"Have you trained the model yet? Error: {e}"
    )

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))                  # wrap raw bytes so PdfReader can open it like a file
    pages  = [page.extract_text() or "" for page in reader.pages]  # extract text from each page — fall back to "" if a page has no text
    return " ".join(pages).strip()                              # join all pages into one string and remove leading/trailing whitespace


def run_classifier(text: str) -> dict:
    """Tokenize text and run the model. Returns label + confidence + all scores."""
    tokens = tokenizer(
        text,
        return_tensors="pt",        # return PyTorch tensors, not plain lists
        padding="max_length",       # pad short texts to exactly max_length tokens
        truncation=True,            # cut texts longer than max_length
        max_length=128              # 128 tokens — enough for most business document snippets
    )
    input_ids      = tokens["input_ids"].to(DEVICE)       # the token IDs — numbers representing each word/subword
    attention_mask = tokens["attention_mask"].to(DEVICE)  # 1 for real tokens, 0 for padding — tells model what to ignore

    with torch.no_grad():                                  # no gradient tracking needed — we're just predicting, not training
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)  # forward pass — get raw scores (logits)

    probs         = torch.softmax(outputs.logits, dim=1)[0]  # convert logits to probabilities that sum to 1
    predicted_idx = probs.argmax().item()                    # index of the highest probability — this is our predicted class

    return {
        "label":      LABEL_NAMES[predicted_idx],                                                    # convert index back to a readable label
        "confidence": round(probs[predicted_idx].item(), 4),                                         # probability of the predicted class
        "all_scores": {LABEL_NAMES[i]: round(probs[i].item(), 4) for i in range(len(LABEL_NAMES))}  # scores for all 4 categories
    }

# ── Request / Response schemas ────────────────────────────────────────────────

class TextInput(BaseModel):                    # defines what the request body must look like for /classify
    text: str                                  # the text to classify — required
    threshold: float = DEFAULT_THRESHOLD       # optional — caller can override the confidence cutoff

class ClassifyResponse(BaseModel):  # defines what /classify sends back
    text: str                       # the original input text
    label: str                      # predicted category — "unknown" if below threshold
    confidence: float               # probability of the predicted category
    all_scores: dict[str, float]    # scores for all 4 categories
    threshold: float                # the threshold that was used for this request

class UploadResponse(BaseModel):    # defines what /upload sends back — same as above plus file info
    filename: str                   # original name of the uploaded file
    extracted_text: str             # preview of the text pulled from the file
    label: str                      # predicted category — "unknown" if below threshold
    confidence: float               # probability of the predicted category
    all_scores: dict[str, float]    # scores for all 4 categories
    threshold: float                # the threshold that was used for this request

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")                   # GET request to the root URL "/"
def root():
    return FileResponse("app/static/index.html")  # serve the frontend HTML page


@app.post("/classify", response_model=ClassifyResponse)  # POST request to "/classify" — expects JSON body
def classify(input: TextInput):                          # FastAPI automatically parses and validates the JSON using TextInput
    if not input.text.strip():                           # reject empty or whitespace-only strings
        raise HTTPException(status_code=400, detail="Text cannot be empty")  # 400 = bad request

    result = run_classifier(input.text)                  # run the model on the text

    # Apply threshold — if model isn't confident enough, return "unknown" instead of a guess
    if result["confidence"] < input.threshold:
        result["label"] = "unknown"                      # override label — better to say unknown than guess wrong

    return ClassifyResponse(text=input.text, threshold=input.threshold, **result)  # include threshold in response so caller knows what was applied


@app.post("/upload", response_model=UploadResponse)      # POST request to "/upload" — expects a file, not JSON
async def upload(file: UploadFile = File(...)):          # async because reading files is I/O — "..." means the field is required
    allowed = ["text/plain", "application/pdf"]          # only accept these two file types
    if file.content_type not in allowed:
        raise HTTPException(                             # reject unsupported formats immediately before reading the file
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Upload a .txt or .pdf file."
        )

    file_bytes = await file.read()                       # read the entire file into memory as raw bytes

    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(file_bytes)         # PDF needs special handling to extract text
    else:
        text = file_bytes.decode("utf-8")                # plain text — just decode bytes to a Python string

    if not text.strip():                                 # catch files that uploaded fine but had no readable text
        raise HTTPException(status_code=400, detail="Could not extract any text from the file.")

    result = run_classifier(text)                        # run the model on the extracted text

    # Apply default threshold for file uploads
    if result["confidence"] < DEFAULT_THRESHOLD:
        result["label"] = "unknown"                      # model not confident enough — don't guess

    return UploadResponse(
        filename=file.filename,                                                    # original filename e.g. "invoice.pdf"
        extracted_text=text[:300] + "..." if len(text) > 300 else text,           # only return first 300 chars — long docs don't need full text in response
        threshold=DEFAULT_THRESHOLD,                                               # always use default threshold for file uploads
        **result                                                                   # unpack label, confidence, all_scores
    )
