import yaml

from fastapi import FastAPI, HTTPException, Response
from app.core.config import settings
from app.models.schemas import NetworkAwarenessResponse, UEPDUSessionReport, QoSRequest
from app.services import translator
from app.services.nrf_manager import nrf_manager
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    await nrf_manager.register_af()
    yield
    # --- Shutdown Logic ---
    await nrf_manager.deregister_af()

app = FastAPI(title="5G QoS Orchestrator AF",
    description="CAMARA-aligned Application Function for UAV QoS Management over free5GC",
              lifespan=lifespan)

# PCF Notification Endpoint
@app.post("/notify", status_code=204)
async def pcf_notify(body: dict):
    """
        for internal use.
    """
    print(f"Received PCF Notification: {body}")
    return Response(status_code=204)

@app.get("/health")
async def health_check():
    """
        Simple health check endpoint to verify the AF is running and can respond to requests.
    """
    return {"status": "connected", "context": "QoS AF Translator"}

# API Placeholders for your Brief
@app.get("/network-awareness", response_model=NetworkAwarenessResponse)
async def get_network_awareness():
    """
        Get a snapshot of the Radio Network Topology.
        Returns gNodeB status, connected UEs, and their active PDU session IPs.
        Use this to identify which UEs are online.
    """
    data = await translator.fetch_network_topology()

    if isinstance(data, dict) and "error" in data:
        raise HTTPException(status_code=502, detail=data["error"])

    return {"radio_map": data}


@app.get("/verify-qos/{supi}", response_model=UEPDUSessionReport)
async def verify_qos(supi: str):
    """
        Retrieve the current QoS status of a UE's PDU sessions.
        Returns active QoS flows, their 5QI values, and whether any GBR profiles are currently applied.
    """
    result = await translator.get_ue_qos_status(supi)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@app.post("/boost-qos")
async def boost_qos(req: QoSRequest):
    """
        Elevate a UE's priority to a GBR (Guaranteed Bit Rate) profile.
        Profiles: EMERGENCY_C2 (5QI 1), VIDEO (5QI 2), UAV_CRITICAL (5QI 3), TELEMETRY (5QI 4).
        Returns an app_session_id required for later release.
    """
    result = await translator.apply_qos_boost(
        supi=req.supi,
        pdu_id=req.pdu_session_id,
        profile_name=req.profile
    )

    if "error" in result:
        # Return 400 or 502 so the Agent knows it's a network/logic failure
        raise HTTPException(status_code=400, detail=result)

    return result


@app.delete("/decrease-qos/{app_session_id}")
async def decrease_qos(app_session_id: str):
    """
        Releases a previously applied QoS boost and returns the UE to default best-effort traffic.
    """
    result = await translator.remove_qos_boost(app_session_id)

    if "error" in result:
        # If it's a 404, we tell the Agent it's already gone
        status_code = 404 if result.get("cause") == "APPLICATION_SESSION_CONTEXT_NOT_FOUND" else 502
        raise HTTPException(status_code=status_code, detail=result)

    # Standard 200 response for successful deletion
    return Response(status_code=200)

@app.get("/openapi.yaml")
def openapi_yaml():
    openapi_schema = app.openapi()
    yaml_str = yaml.dump(openapi_schema)
    return Response(content=yaml_str, media_type="application/yaml")