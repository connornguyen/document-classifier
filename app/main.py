import io
import torch
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pypdf import PdfReader

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Document Classifier API",
    description="Classifies business documents into Invoice, Contract, Report, or Email.",
    version="4.0.0"
)

# Minimum confidence required to return a label — below this returns "unknown"
DEFAULT_THRESHOLD = 0.6

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ── Model ─────────────────────────────────────────────────────────────────────
# Loaded once at startup to avoid reloading on every request

MODEL_PATH  = "./models/distilbert-business"
LABEL_NAMES = ["Invoice", "Contract", "Report", "Email"]
DEVICE      = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model     = model.to(DEVICE)
    model.eval()
    print(f"Model loaded on {DEVICE}")
except Exception as e:
    raise RuntimeError(
        f"Could not load model from '{MODEL_PATH}'. "
        f"Have you trained the model yet? Error: {e}"
    )

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract and concatenate text from all pages of a PDF."""
    reader = PdfReader(io.BytesIO(file_bytes))
    pages  = [page.extract_text() or "" for page in reader.pages]
    return " ".join(pages).strip()


def run_classifier(text: str) -> dict:
    """
    Tokenize input text and run inference.
    Returns predicted label, confidence score, and scores for all categories.
    """
    tokens = tokenizer(
        text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=128
    )
    input_ids      = tokens["input_ids"].to(DEVICE)
    attention_mask = tokens["attention_mask"].to(DEVICE)

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)

    probs         = torch.softmax(outputs.logits, dim=1)[0]
    predicted_idx = probs.argmax().item()

    return {
        "label":      LABEL_NAMES[predicted_idx],
        "confidence": round(probs[predicted_idx].item(), 4),
        "all_scores": {LABEL_NAMES[i]: round(probs[i].item(), 4) for i in range(len(LABEL_NAMES))}
    }

# ── Schemas ───────────────────────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str
    threshold: float = DEFAULT_THRESHOLD


class ClassifyResponse(BaseModel):
    text: str
    label: str
    confidence: float
    all_scores: dict[str, float]
    threshold: float


class UploadResponse(BaseModel):
    filename: str
    extracted_text: str
    label: str
    confidence: float
    all_scores: dict[str, float]
    threshold: float

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse("app/static/index.html")


@app.post("/classify", response_model=ClassifyResponse)
def classify(input: TextInput):
    """Classify raw text. Returns label and confidence score."""
    if not input.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    result = run_classifier(input.text)

    if result["confidence"] < input.threshold:
        result["label"] = "unknown"

    return ClassifyResponse(text=input.text, threshold=input.threshold, **result)


@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    """Accept a .txt or .pdf file, extract its text, and classify it."""
    allowed = ["text/plain", "application/pdf"]
    if file.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Upload a .txt or .pdf file."
        )

    file_bytes = await file.read()

    if file.content_type == "application/pdf":
        text = extract_text_from_pdf(file_bytes)
    else:
        text = file_bytes.decode("utf-8")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract any text from the file.")

    result = run_classifier(text)

    if result["confidence"] < DEFAULT_THRESHOLD:
        result["label"] = "unknown"

    return UploadResponse(
        filename=file.filename,
        extracted_text=text[:300] + "..." if len(text) > 300 else text,
        threshold=DEFAULT_THRESHOLD,
        **result
    )
