FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose backend (8000) and frontend (8501) ports
EXPOSE 8000
EXPOSE 8501

# Default command launches the backend server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
