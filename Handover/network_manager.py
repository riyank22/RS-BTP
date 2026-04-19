import subprocess
import time
import re
import requests

class NetworkManager:
    def __init__(self, hysteresis=5.0, rs_threshold=-110.0):
        self.active_connections = {}
        self.hysteresis = hysteresis
        self.rs_threshold = rs_threshold
        self.WEBUI_NOTIF_URL = "http://localhost:8004/api/notify"

    def _send_notification(self, message):
        """Sends a real-time log string to the WebUI backend."""
        try:
            # Assuming a simple JSON body { "message": "..." }
            # or adjust based on your FastAPI model
            requests.post(self.WEBUI_NOTIF_URL, json={"content": message}, timeout=1)
        except Exception as e:
            print(f"   [WebUI-Link] Failed to send notification: {e}")

    def _extract_id(self, string):
        """
        Extracts the numeric ID from gnb-X or imsi-20893000000000X.
        Returns the last non-zero digit or the tailing number.
        """
        match = re.search(r'(\d+)$', string)
        if match:
            # For gnb-1 -> 1, for imsi-...002 -> 2
            return match.group(1).lstrip('0') or '0'
        return None

    def _extract_ue_id(self, string):
        """
        Extracts the numeric ID imsi-20893000000000X to X.
        Returns the last non-zero digit or the tailing number.
        Remove the imsi-5digits then we are left with 000000000X, we want to extract the X.
        """
        match = re.search(r'imsi-\d{5}(\d+)$', string)
        if match:
            return match.group(1).lstrip('0') or '0'
        return None

    def _execute_cmd(self, cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"   [Error] {result.stderr.strip()}")
            return result.returncode == 0
        except Exception as e:
            print(f"   [Exception] {e}")
            return False

    def trigger_action(self, ue_full_id, gnb_full_id, action_type, reason="", old_gnb_full_id=None):
        ue_id = self._extract_ue_id(ue_full_id)
        gnb_container = f"gnb{self._extract_id(gnb_full_id)}"
        if old_gnb_full_id is not None: old_gnb_full_id = f"gnb{self._extract_id(old_gnb_full_id)}"
        config_file = f"ue{ue_id}cfg.yaml"

        print(f"\n📢 >>> [NETWORK ACTION: {action_type}] <<<")
        print(f"   Target UE: {ue_full_id} (Config: {config_file})")
        print(f"   Target Container: {gnb_container}")
        if reason: print(f"   Reason: {reason}")

        binary_path = "./nr-ue"

        if action_type == "START":
            cmd = ["docker", "exec", "-d", gnb_container, binary_path, "-c", f"config/{config_file}"]
            print(f"command executed: {cmd}")
            if self._execute_cmd(cmd):
                self._send_notification(f"✅ Session Active: {ue_full_id} is now LIVE on {gnb_full_id}.")
                print(f"   [OK] Session started on {gnb_container}")
            # print(f"   CMD: docker exec -it {gnb_container} ./nr-ue -c config/{ue_id}.yaml")

        elif action_type == "HANDOVER":
            print(f"   [Handover] Killing session on {old_gnb_full_id}...")
            kill_cmd = ["docker", "exec", old_gnb_full_id, "pkill", "-f", config_file]
            self._execute_cmd(kill_cmd)
            time.sleep(1)
            print(f"   [Handover] Starting session on {gnb_container}...")
            start_cmd = ["docker", "exec", "-d", gnb_container, binary_path, "-c", f"config/{config_file}"]
            if self._execute_cmd(start_cmd):
                self._send_notification(f"🎯 Handover triggered for {ue_full_id}. Migrated from {old_gnb_full_id} to {gnb_full_id}.")
                print(f"   [OK] Handover successful.")

        elif action_type == "STOP":
            cmd = ["docker", "exec", gnb_container, "pkill", "-f", config_file]
            if self._execute_cmd(cmd):
                msg = f"🛑 Disconnecting: UE {ue_full_id} leaving coverage of {gnb_full_id}."
                self._send_notification(msg)
                print(f"   [OK] Session stopped.")

    def update_state(self, ue_id, best_gnb, best_rsrp, current_rsrp):
        current_gnb = self.active_connections.get(ue_id)

        # 1. New Connection
        if current_gnb is None and best_gnb:
            self.trigger_action(ue_id, best_gnb, "START", "Initial entry into coverage zone.")
            self.active_connections[ue_id] = best_gnb

        # 2. Connection Lost
        elif current_gnb and (best_gnb is None or best_rsrp < self.rs_threshold):
            self.trigger_action(ue_id, current_gnb, "STOP", "UE moved out of all tower ranges.")
            del self.active_connections[ue_id]

        # 3. Handover Check with Hysteresis Logging
        elif current_gnb and best_gnb and current_gnb != best_gnb:
            gain = best_rsrp - current_rsrp
            print(f"   [Decision] Handover Evaluation: Potential Gain = {gain:.2f} dB (Required: {self.hysteresis} dB)")

            if gain > self.hysteresis:
                self.trigger_action(ue_id, best_gnb, "HANDOVER", f"Gain {gain:.2f}dB exceeds hysteresis.", old_gnb_full_id=current_gnb)
                self.active_connections[ue_id] = best_gnb
            else:
                print(f"   [Decision] Handover REJECTED: Gain insufficient to trigger switch.")