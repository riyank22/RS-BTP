# api/routes/notifications.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.websocket import manager

router = APIRouter()


@router.websocket("/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/notify")
async def relay_system_message(payload: dict):
    """
    Expects JSON like: {"type": "HANDOVER", "data": {"from": "gnb1", "to": "gnb2"}}
    """
    if "type" not in payload:
        payload = {"type": "SYSTEM_ALERT", "data": payload}

    await manager.broadcast(payload)
    return {"status": "broadcasted"}