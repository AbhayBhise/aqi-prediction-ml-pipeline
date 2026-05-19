FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=7860

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["gunicorn", "--worker-class=gthread", "--workers=1", "--threads=8", "--timeout=180", "--bind=0.0.0.0:7860", "--chdir", "backend/api", "app:app"]
