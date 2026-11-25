FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlit UI port
EXPOSE 8501

# XSRF/CORS are disabled so file uploads work behind the Codespaces port-forwarding proxy
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false", "--server.enableCORS=false"]
