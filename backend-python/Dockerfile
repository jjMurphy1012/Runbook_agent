FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Build context is the repo root; see docker-compose.yml.
COPY backend-python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend-python/ ./
COPY data/ /app/data/
COPY scripts/ /app/scripts/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
