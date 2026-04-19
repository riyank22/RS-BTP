import asyncio

import httpx
from app.core.config import settings
import logging
from app.core.constants import QOS_TEMPLATES

logger = logging.getLogger(__name__)

import httpx
import asyncio
from app.core.config import settings


async def fetch_network_topology():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            # Step 1 & 2: Get gNB list and global UE context concurrently
            gnb_task = client.get(f"{settings.AMF_URL}/namf-oam/v1/registered-gnb-context", timeout=3.0)
            ue_task = client.get(f"{settings.AMF_URL}/namf-oam/v1/registered-ue-context", timeout=3.0)

            gnb_resp, ue_resp = await asyncio.gather(gnb_task, ue_task)
            gnb_resp.raise_for_status()
            ue_resp.raise_for_status()

            raw_gnbs = gnb_resp.json()
            raw_ue_contexts = ue_resp.json()  # List of all UEs and their PDU session IDs
        except Exception as e:
            return {"error": f"Failed to reach AMF: {str(e)}"}

        # Map SUPI to their PDU Session IDs for quick lookup
        ue_session_map = {u["Supi"]: u.get("PduSessions", []) for u in raw_ue_contexts}

        # Step 3: Deep-fetch SMF data for every active PDU session found
        all_smf_tasks = []
        task_metadata = []  # To keep track of which SUPI/ID belongs to which task

        for supi, sessions in ue_session_map.items():
            for sess in sessions:
                sid = sess["PduSessionId"]
                url = f"{settings.SMF_URL}/nsmf-oam/v1/ue-qos-info/{supi}/{sid}"
                all_smf_tasks.append(client.get(url, timeout=2.0))
                task_metadata.append((supi, sid))

        smf_responses = await asyncio.gather(*all_smf_tasks, return_exceptions=True)

        # Organize SMF data: {supi: [session_data_1, session_data_2]}
        smf_data_map = {}
        for i, resp in enumerate(smf_responses):
            if isinstance(resp, httpx.Response) and resp.status_code == 200:
                data = resp.json()
                supi, sid = task_metadata[i]

                # Logic: Find the "Best" (lowest) 5QI in this session
                flows = data.get("QoSFlows", [])
                if flows:
                    # Sort by 5QI value ascending
                    best_flow = sorted(flows, key=lambda x: x.get("5QI", 99))[0]
                else:
                    best_flow = {"5QI": 9, "QFI": 0, "5QILabel": "Unknown"}

                session_summary = {
                    "pdu_session_id": sid,
                    "pdu_address": data.get("PDUAddress"),
                    "dnn": data.get("Dnn"),
                    "best_5qi": best_flow.get("5QI"),
                    "qfi": best_flow.get("QFI"),
                    "label": best_flow.get("5QILabel"),
                    "max_br_ul": best_flow.get("MaxBitrateUL", "N/A"),
                    "max_br_dl": best_flow.get("MaxBitrateDL", "N/A")
                }

                if supi not in smf_data_map:
                    smf_data_map[supi] = []
                smf_data_map[supi].append(session_summary)

        # Final Assembly: Build the Topology based on gNB grouping
        topology = []
        for gnb in raw_gnbs:
            gnb_id = gnb.get("GnbId")
            connected_ues = []

            if gnb.get("ConnectedUEs"):
                for ue in gnb["ConnectedUEs"]:
                    supi = ue.get("Supi")
                    connected_ues.append({
                        "supi": supi,
                        "state": ue.get("CmState"),
                        "pdu_sessions": smf_data_map.get(supi, [])
                    })

            topology.append({
                "gnb_id": gnb_id,
                "name": gnb.get("Name"),
                "n2_ip": gnb.get("N2IP"),
                "ue_count": gnb.get("UeCount", 0),
                "connected_ues": connected_ues
            })

        return topology


async def get_ue_qos_status(supi: str):
    # Step 1: Query AMF for PDU Session List
    amf_url = f"{settings.AMF_URL}/namf-oam/v1/registered-ue-context/{supi}"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            amf_resp = await client.get(amf_url, timeout=2.0)
            amf_resp.raise_for_status()
            ue_context_list = amf_resp.json()

            # The AMF returns a list of contexts (usually one for 3GPP access)
            if not ue_context_list:
                return {"error": "UE context not found in AMF"}

            ue_data = ue_context_list[0]
            pdu_sessions = ue_data.get("PduSessions", [])

        except Exception as e:
            return {"error": f"AMF Lookup Failed: {str(e)}"}

        # Step 2: Query SMF for details on EACH PDU Session
        qos_report = []

        async def fetch_smf_details(session_id):
            smf_url = f"{settings.SMF_URL}/nsmf-oam/v1/ue-qos-info/{supi}/{session_id}"
            try:
                smf_resp = await client.get(smf_url, timeout=2.0)
                if smf_resp.status_code == 200:
                    s_data = smf_resp.json()

                    # Map the SMF QoS Flows
                    flows = [
                        {
                            "qfi": f.get("QFI"),
                            "five_qi": f.get("5QI"),
                            "label": f.get("5QILabel"),
                            "is_default": f.get("IsDefault", False)
                        } for f in s_data.get("QoSFlows", [])
                    ]

                    return {
                        "pdu_session_id": session_id,
                        "pdu_address": s_data.get("PDUAddress"),
                        "dnn": s_data.get("Dnn"),
                        "default_5qi": s_data.get("Default5QI"),
                        "active_flows": flows
                    }
            except Exception:
                return None

        # Execute SMF calls in parallel for efficiency
        tasks = [fetch_smf_details(s["PduSessionId"]) for s in pdu_sessions]
        results = await asyncio.gather(*tasks)

        # Filter out failed SMF lookups
        qos_report = [r for r in results if r is not None]

        return {
            "supi": supi,
            "pdu_sessions": qos_report
        }


logger = logging.getLogger(__name__)


async def apply_qos_boost(supi: str, pdu_id: str, profile_name: str):
    # 1. Validate Profile
    template = QOS_TEMPLATES.get(profile_name)
    if not template:
        return {"error": f"Invalid QoS Profile: {profile_name}"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        # 2. STEP A: Get UE IP from SMF OAM
        smf_url = f"{settings.SMF_URL}/nsmf-oam/v1/ue-qos-info/{supi}/{pdu_id}"
        try:
            smf_resp = await client.get(smf_url, timeout=3.0)
            smf_resp.raise_for_status()
            ue_ip = smf_resp.json().get("PDUAddress")
            if not ue_ip:
                return {"error": "Could not retrieve UE IP from SMF"}
        except Exception as e:
            return {"error": f"SMF Lookup Failed: {str(e)}"}

        # 3. STEP B: Build the Verbose PCF Payload
        pcf_payload = {
            "ascReqData": {
                "ueIpv4": ue_ip,
                "notifUri": f"http://{settings.HOST_IP}:8000/notify",
                "suppFeat": "1",
                "medComponents": {
                    "1": {
                        "medCompN": 1,
                        "medType": template["medType"],
                        "fStatus": "ENABLED",
                        "marBwUl": template["marBw"],
                        "marBwDl": template["marBw"],
                        "mirBwUl": template["mirBw"],
                        "mirBwDl": template["mirBw"],
                        "resQos": {
                            "5qi": template["5qi"],
                            "arp": {
                                "priorityLevel": template["priority"],
                                "preemptCap": "NOT_PREEMPT",
                                "preemptVuln": "NOT_PREEMPTABLE"
                            }
                        },
                        "medSubComps": {
                            "1": {
                                "fNum": 1,
                                "fStatus": "ENABLED",
                                "fDescs": [f"permit out {ue_ip} from any to assigned"]
                            }
                        }
                    }
                }
            }
        }

        # 4. STEP C: Fire PCF Policy Authorization
        pcf_url = f"{settings.PCF_URL}/npcf-policyauthorization/v1/app-sessions"
        try:
            pcf_resp = await client.post(pcf_url, json=pcf_payload, timeout=5.0)

            # 3GPP SUCCESS: 201 Created
            if pcf_resp.status_code == 201:
                # Extract Location Header: .../app-sessions/{appSessionId}
                location = pcf_resp.headers.get("Location", "")
                app_session_id = location.split("/")[-1] if location else "unknown"

                return {
                    "status": "success",
                    "message": "QoS Boost Applied",
                    "app_session_id": app_session_id,
                    "ue_ip": ue_ip,
                    "target_5qi": template["5qi"],
                    "pcf_response": pcf_resp.json()
                }
            else:
                return {
                    "error": f"PCF Rejected Policy: {pcf_resp.status_code}",
                    "details": pcf_resp.text
                }
        except Exception as e:
            return {"error": f"PCF Connection Failed: {str(e)}"}


async def remove_qos_boost(app_session_id: str):
    # The resource URL is the base app-sessions + the ID
    url = f"{settings.PCF_URL}/npcf-policyauthorization/v1/app-sessions/{app_session_id}/delete"

    async with httpx.AsyncClient() as client:
        try:
            # Using POST as per your 3GPP lab fix
            response = await client.post(url, timeout=3.0)

            print(f"DEBUG: PCF Response Status: {response.status_code}")

            if response.status_code == 204:
                return {"status": "success", "id": app_session_id}

            elif response.status_code == 404:
                return {
                    "error": "Session Not Found",
                    "cause": "APPLICATION_SESSION_CONTEXT_NOT_FOUND"
                }
            else:
                return {"error": f"PCF error {response.status_code}", "details": response.text}

        except Exception as e:
            return {"error": f"Connection to PCF failed: {str(e)}"}