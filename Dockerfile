FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=7860

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --default-timeout=2000 --retries=10 --no-cache-dir numpy==2.2.6 pandas==2.3.3 scipy==1.15.3 scikit-learn==1.7.2 xgboost==3.2.0 lightgbm==4.3.0
RUN pip install --default-timeout=2000 --retries=10 --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["gunicorn", "--worker-class=gthread", "--workers=1", "--threads=8", "--timeout=180", "--bind=0.0.0.0:7860", "--chdir", "backend/api", "app:app"]
