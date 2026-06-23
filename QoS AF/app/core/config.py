from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Free5GC NF Endpoints (Defaults to local for dev)
    AMF_URL: str = "http://10.100.200.16:8000"
    PCF_URL: str = "http://10.100.200.13:8000"
    SMF_URL: str = "http://10.100.200.11:8000"
    NRF_URL: str = "http://10.100.200.4:8000"
    HOST_IP: str = "10.100.200.1"
    LOCATION_AF_URL: str = "http://127.0.0.1:8001"
    
    # App Settings
    APP_NAME: str = "CAMARA-QoS-AF"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()