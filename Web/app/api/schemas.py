from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- Drone / Location Schemas ---

class Coordinate(BaseModel):
    lat: float
    lng: float

class DroneLocationUpdate(BaseModel):
    """Payload received from Frontend and relayed to Location AF"""
    id: str = Field(..., description="The SUPI of the drone (e.g., imsi-...)")
    lat: float
    lng: float

# --- QoS / Network Schemas (For Response Typing) ---

class PDUSession(BaseModel):
    pdu_session_id: str
    pdu_address: str
    dnn: str
    best_5qi: Optional[int] = None
    qfi: Optional[int] = None
    label: Optional[str] = None

class UEConnected(BaseModel):
    supi: str
    state: str
    pdu_sessions: List[PDUSession]
    # Enriched fields added by our relay
    lat: Optional[float] = None
    lng: Optional[float] = None

class GnodeB(BaseModel):
    gnb_id: str
    name: str
    n2_ip: str
    ue_count: int
    connected_ues: List[UEConnected]
    # Enriched metadata from Location AF
    location: Optional[Dict[str, Any]] = None

# --- Agent / Path Schemas ---

class PathRequest(BaseModel):
    start: Coordinate
    end: Coordinate

class AgentThought(BaseModel):
    thought: Optional[str] = None
    path: Optional[List[List[float]]] = None