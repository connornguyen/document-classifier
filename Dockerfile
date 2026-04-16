# Base image — Python 3.11 slim keeps the image size small
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy and install dependencies first — Docker caches this layer
# so rebuilds are fast as long as requirements.txt hasn't changed
# Use CPU-only torch to keep image size small — MPS/CUDA not available in containers
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy the rest of the project
COPY app/ ./app/
COPY models/ ./models/

# Expose the port the API runs on
EXPOSE 8000

# Start the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
