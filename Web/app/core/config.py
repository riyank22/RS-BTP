import os

# Base URLs for the microservices
QOS_URL = os.getenv("QOS_SERVICE_URL", "http://localhost:8000")
LOC_URL = os.getenv("LOC_SERVICE_URL", "http://localhost:8001")
AGENT_URL = os.getenv("AGENT_SERVICE_URL", "http://localhost:8002")

# Timeout settings for internal API calls
API_TIMEOUT = 5.0