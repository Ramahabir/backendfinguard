# syntax=docker/dockerfile:1

# Lightweight Python base image
FROM python:3.12-slim AS runtime

# Environment settings for reliable, unbuffered Python logs
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files explicitly (as requested)
COPY main.py analyze.py ./

# Optionally pass Google API key at runtime: -e GOOGLE_API_KEY=...
ENV PORT=8000
EXPOSE 8000

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8000"]

