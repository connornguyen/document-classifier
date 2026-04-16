# Base image — Python 3.11 slim keeps the image size small
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy and install dependencies first — Docker caches this layer
# so rebuilds are fast as long as requirements-docker.txt hasn't changed
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy app code
COPY app/ ./app/

# Download the model from HuggingFace Hub at build time
# This keeps model files out of git while still baking them into the image
RUN python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='connorbuild/document-classifier',
    local_dir='./models/distilbert-business'
)
print('Model downloaded successfully')
"

# Expose the port the API runs on
EXPOSE 8000

# Start the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
