from fastapi import APIRouter, HTTPException
import httpx
import asyncio
from core.config import QOS_URL, LOC_URL

router = APIRouter()


@router.get("/network-details")
async def get_details():
    async with httpx.AsyncClient() as client:
        # Parallel calls to all sources
        tasks = [
            client.get(f"{QOS_URL}/network-awareness"),
            client.get(f"{LOC_URL}/location/get-ues"),
            client.get(f"{LOC_URL}/location/get-gnbs"),
            client.get(f"{LOC_URL}/zones")
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Helper to safely extract JSON or return empty structure
        def safe_json(res, default):
            return res.json() if not isinstance(res, Exception) and res.status_code == 200 else default

        qos_data = safe_json(results[0], {"radio_map": []})
        ue_locs = safe_json(results[1], [])
        gnb_locs = safe_json(results[2], [])
        zones = safe_json(results[3], [])

        # 1. Create Lookup Maps for O(1) merging
        # Note: Mapping gnb-1 -> UERANSIM-gnb-208-93-1 logic
        # We'll use the last digit of the gnb_id string to match if names differ
        ue_map = {u['ue_id']: u for u in ue_locs}
        gnb_loc_map = {g['gnb_id']: g for g in gnb_locs}

        final_gnbs = []
        final_ues = []

        # 2. Process GnBs and their connected UEs
        for g_core in qos_data.get("radio_map", []):
            # Extract numerical suffix to match 'gnb-1' from location AF
            core_id_str = g_core['gnb_id']  # e.g., "00000001"
            short_id = f"gnb-{int(core_id_str)}"

            loc_info = gnb_loc_map.get(short_id, {})

            # Prepare Enriched GnB Object
            gnb_obj = {
                "gnb_id": core_id_str,
                "name": g_core.get("name"),
                "n2_ip": g_core.get("n2_ip"),
                "ue_count": g_core.get("ue_count", 0),
                "lat": loc_info.get("lat"),
                "lng": loc_info.get("lng"),
                "radius": loc_info.get("radius", 3000),
            }

            # 3. Process UEs connected to this specific GnB
            for ue_core in g_core.get("connected_ues", []):
                supi = ue_core['supi']
                u_loc = ue_map.get(supi, {})

                ue_obj = {
                    "supi": supi,
                    "state": ue_core.get("state"),
                    "pdu_sessions": ue_core.get("pdu_sessions", []),
                    "lat": u_loc.get("lat"),
                    "lng": u_loc.get("lng"),
                    "timestamp": u_loc.get("timestamp"),
                    "connected_to": core_id_str
                }

                final_ues.append(ue_obj)  # Also add to a flat list for global tracking

            final_gnbs.append(gnb_obj)

        # 4. Final Response
        return {
            "gnbs": final_gnbs,
            "ues": final_ues,
            "restricted_areas": zones,
            "timestamp": asyncio.get_event_loop().time()
        }


@router.get("/ue-stats/{supi}")
async def get_stats(supi: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{QOS_URL}/verify-qos/{supi}")
        return resp.json()