import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Document Classifier API",
    description="Classifies text into World, Sports, Business, or Sci/Tech",
    version="2.0.0"
)

# ── Load model once at startup ────────────────────────────────────────────────
# Loading a model is expensive (~1-2 seconds).
# We do it ONCE when the server starts — not on every request.
# If we loaded it inside classify(), every single request would take 2 extra seconds.

MODEL_PATH  = "./models/distilbert-ag-news"
LABEL_NAMES = ["World", "Sports", "Business", "Sci/Tech"]
DEVICE      = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model     = model.to(DEVICE)
    model.eval()  # set to eval mode — disables dropout, makes inference faster
    print(f"Model loaded on {DEVICE}")
except Exception as e:
    # If the model isn't found, give a clear error instead of a cryptic crash
    raise RuntimeError(
        f"Could not load model from '{MODEL_PATH}'. "
        f"Have you run the Day 5 notebook yet? Error: {e}"
    )

# ── Request / Response schemas ────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str

class ClassifyResponse(BaseModel):
    text: str
    label: str
    confidence: float
    all_scores: dict[str, float]

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "message": "Document Classifier API is running"}


@app.post("/classify", response_model=ClassifyResponse)
def classify(input: TextInput):
    # Guard against empty input
    if not input.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Tokenize — same as predict() in Day 5
    tokens = tokenizer(
        input.text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=128
    )
    input_ids      = tokens["input_ids"].to(DEVICE)
    attention_mask = tokens["attention_mask"].to(DEVICE)

    # Forward pass — no gradient tracking needed for inference
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)

    # logits → probabilities → label
    probs         = torch.softmax(outputs.logits, dim=1)[0]
    predicted_idx = probs.argmax().item()

    return ClassifyResponse(
        text       = input.text,
        label      = LABEL_NAMES[predicted_idx],
        confidence = round(probs[predicted_idx].item(), 4),
        all_scores = {LABEL_NAMES[i]: round(probs[i].item(), 4) for i in range(len(LABEL_NAMES))}
    )
