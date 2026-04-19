from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union, Dict

class LocationUpdate(BaseModel):
    id: str  # IMSI
    lat: float
    lng: float

class GeofenceSchema(BaseModel):
    zone_id: str
    zone_type: str
    shape: str
    data: Dict

class UEResponse(BaseModel):
    ue_id: str
    lat: float
    lng: float
    timestamp: datetime # Changed from str to datetime

    class Config:
        from_attributes = True