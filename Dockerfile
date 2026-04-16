# Base image — Python 3.11 slim keeps the image size small
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy and install dependencies first — Docker caches this layer
# so rebuilds are fast as long as requirements-docker.txt hasn't changed
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy app code and download script
COPY app/ ./app/
COPY scripts/download_model.py ./scripts/download_model.py

# Download the model from HuggingFace Hub at build time
RUN python scripts/download_model.py

# Expose the port the API runs on
EXPOSE 8000

# Start the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
