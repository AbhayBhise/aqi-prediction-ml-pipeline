from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest
import time

app = Flask(__name__)

# 1. Define Prometheus Metrics
REQUEST_COUNT = Counter(
    'api_request_total',
    'Total number of requests received',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'API request latency in seconds',
    ['endpoint']
)

PREDICTION_HISTOGRAM = Histogram(
    'aqi_prediction_value',
    'Distribution of predicted AQI values',
    buckets=[0, 50, 100, 150, 200, 300, 500]
)

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    
    # ... your existing model prediction logic here ...
    # e.g., dummy prediction for example
    predicted_aqi = 120.5 
    
    # 2. Record Metrics
    PREDICTION_HISTOGRAM.observe(predicted_aqi)
    REQUEST_COUNT.labels(method='POST', endpoint='/predict', http_status=200).inc()
    REQUEST_LATENCY.labels(endpoint='/predict').observe(time.time() - start_time)
    
    return jsonify({"predicted_aqi": predicted_aqi})

# 3. Expose the /metrics endpoint for Prometheus to scrape
@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
