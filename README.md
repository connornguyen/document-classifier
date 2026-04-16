# Document Classifier

A REST API that classifies business documents into 4 categories using a fine-tuned DistilBERT model.

**Categories:** Invoice · Contract · Report · Email

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/document-classifier.git
cd document-classifier

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Generate training data and train the model:
```bash
python scripts/generate_data.py
# then run notebooks/day8_business_classifier.ipynb
```

---

## Run the API

```bash
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

---

## Usage

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Invoice #1234 for consulting services totalling $5,000. Payment due in 30 days."}'
```

**Response:**
```json
{
  "text": "Invoice #1234 for consulting services totalling $5,000. Payment due in 30 days.",
  "label": "Invoice",
  "confidence": 0.9008,
  "all_scores": {
    "Invoice": 0.9008,
    "Contract": 0.0371,
    "Report": 0.0223,
    "Email": 0.0398
  }
}
```

---

## Stack

- **Model:** DistilBERT fine-tuned on synthetic business documents
- **API:** FastAPI + Uvicorn
- **Framework:** PyTorch + HuggingFace Transformers
