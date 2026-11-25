# Lightweight Python base image (same Python minor version family as Colab)
FROM python:3.11-slim

# Working directory inside the container
WORKDIR /app

# Install dependencies first (cached layer if requirements don't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app and the serialized model
COPY . .

# Flask API port
EXPOSE 7860

# Serve with gunicorn: 2 workers, bound to all interfaces on port 7860
CMD ["gunicorn", "--workers", "2", "--timeout", "120", "--bind", "0.0.0.0:7860", "app:superkart_api"]
