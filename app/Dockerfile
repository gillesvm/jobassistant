FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for Docker layer caching optimization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port (must match containerPort in ecs.tf)
EXPOSE 8000

# Start Uvicorn bound to all interfaces
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--forwarded-allow-ips", "*"]
