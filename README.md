# Document Classifier

A REST API that classifies business documents into 4 categories using a fine-tuned DistilBERT model.

**Categories:** Invoice · Contract · Report · Email

## Live Demo

**https://document-classifier-1z1s.onrender.com**

> Hosted on Render free tier — may take ~30 seconds to wake up if inactive.

---

## Run with Docker

```bash
docker run -d -p 8000:8000 connorbuilds/document-classifier
```

Open `http://localhost:8000` — no setup required.

---

## Development Setup

```bash
git clone https://github.com/connornguyen/document-classifier.git
cd document-classifier
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Stack

- **Model:** DistilBERT fine-tuned on synthetic business documents — [connorbuild/document-classifier](https://huggingface.co/connorbuild/document-classifier)
- **API:** FastAPI + Uvicorn
- **Framework:** PyTorch + HuggingFace Transformers
- **Containerisation:** Docker — [connorbuilds/document-classifier](https://hub.docker.com/r/connorbuilds/document-classifier)
- **Deployment:** Render
