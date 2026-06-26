from prometheus_client import Counter, Histogram, Gauge

# HTTP Request Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

# Application Domain Metrics
simulations_run_total = Counter(
    "simulations_run_total",
    "Total number of Digital Twin simulations executed",
    ["scenario_type"]
)

model_training_duration_seconds = Histogram(
    "model_training_duration_seconds",
    "Time taken to train ML models",
    ["algorithm", "target_variable"]
)

dataset_ingestion_errors_total = Counter(
    "dataset_ingestion_errors_total",
    "Total number of errors during dataset ingestion pipeline",
    ["dataset_source"]
)

active_websocket_connections = Gauge(
    "active_websocket_connections",
    "Number of active WebSocket connections to the Digital Twin dashboard"
)
