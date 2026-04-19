from pydantic import BaseModel
from typing import List, Optional

class UESummary(BaseModel):
    supi: str
    state: str

class GNodeBResponse(BaseModel):
    gnb_id: str
    name: str
    ue_count: int
    connected_ues: List[UESummary]

class PDUSessionMinimal(BaseModel):
    pdu_session_id: str
    pdu_address: Optional[str]
    dnn: str
    best_5qi: int  # The lowest 5QI value in the session
    qfi: int
    label: str
    max_br_ul: str
    max_br_dl: str

class UETopology(BaseModel):
    supi: str
    state: str
    pdu_sessions: List[PDUSessionMinimal]

class GNodeBTopology(BaseModel):
    gnb_id: str
    name: str
    n2_ip: str
    ue_count: int
    connected_ues: List[UETopology]

class NetworkAwarenessResponse(BaseModel):
    radio_map: List[GNodeBTopology]

class QoSFlowSummary(BaseModel):
    qfi: int
    five_qi: int
    label: Optional[str] = None
    is_default: bool

class PDUSessionQoS(BaseModel):
    pdu_session_id: str
    pdu_address: Optional[str] = None
    dnn: str
    default_5qi: int
    active_flows: List[QoSFlowSummary]

class UEPDUSessionReport(BaseModel):
    supi: str
    pdu_sessions: List[PDUSessionQoS]

class QoSRequest(BaseModel):
    supi: str
    pdu_session_id: str
    profile: str # e.g., "HD_VIDEO" or "CRITICAL_UAV"