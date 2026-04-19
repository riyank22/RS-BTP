import httpx
import asyncio
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class NRFManager:
    def __init__(self):
        self.instance_id = "550e8400-e29b-41d4-a716-446655440000"
        self.nrf_url = f"{settings.NRF_URL}/nnrf-nfm/v1/nf-instances/{self.instance_id}"
        self.heartbeat_interval = 50

    async def register_af(self):
        nf_profile = {
            "nfInstanceId": self.instance_id,
            "nfType": "AF",
            "nfStatus": "REGISTERED",
            "ipv4Addresses": [settings.HOST_IP],
            "heartBeatTimer": 60,
            "plmnList": [{"mcc": "208", "mnc": "93"}],
            "nfServices": [
                {
                    "serviceInstanceId": "camara-qos-v1",
                    "serviceName": "af_qos",
                    "versions": [{"apiVersionInUri": "v1", "svcVersion": "1.0.0"}],
                    "scheme": "http",
                    "nfServiceStatus": "REGISTERED",
                    "ipEndPoints": [{"ipv4Address": settings.HOST_IP, "port": 8000}]
                }
            ]
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(self.nrf_url, json=nf_profile)
                response.raise_for_status()
                logger.info(f"Successfully registered to NRF at {settings.NRF_URL}")
                # Start heartbeat after successful registration
                asyncio.create_task(self.run_heartbeat())
            except Exception as e:
                logger.error(f"NRF Registration Failed: {e}")

    async def run_heartbeat(self):
        patch_data = [{"op": "replace", "path": "/nfStatus", "value": "REGISTERED"}]
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            async with httpx.AsyncClient() as client:
                try:
                    await client.patch(self.nrf_url, json=patch_data)
                except Exception:
                    logger.warning("NRF Heartbeat failed. Will retry.")

    async def deregister_af(self):
        async with httpx.AsyncClient() as client:
            try:
                await client.delete(self.nrf_url)
                logger.info("Deregistered from NRF.")
            except Exception as e:
                logger.error(f"Deregistration failed: {e}")

nrf_manager = NRFManager()