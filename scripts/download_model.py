from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="connorbuild/document-classifier",
    local_dir="./models/distilbert-business"
)
print("Model downloaded successfully")
