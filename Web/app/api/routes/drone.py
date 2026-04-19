from fastapi import APIRouter, HTTPException
import httpx
from api.schemas import DroneLocationUpdate
from core.config import LOC_URL, API_TIMEOUT

router = APIRouter()


@router.post("/update-location")
async def relay_drone_location(data: DroneLocationUpdate):
    """
    Acts as a relay: Frontend -> Web Backend -> Location AF
    """
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        try:
            # We match the exact payload structure your Location AF expects
            # curl -d '{"id": "...", "lat": 0, "lng": 0}'
            response = await client.post(
                f"{LOC_URL}/location/update",
                json=data.dict()
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Location AF failed to update"
                )

            return response.json()

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Location AF is unreachable: {exc}"
            )