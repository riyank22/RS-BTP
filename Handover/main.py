import time
import requests
from physics_engine import PhysicsEngine
from network_manager import NetworkManager

LOCATION_AF_URL = "http://localhost:8001"
POLL_INTERVAL = 30

physics = PhysicsEngine()
net_mgr = NetworkManager(hysteresis=5.0)


def orchestrate():
    timestamp = time.strftime('%H:%M:%S')
    print(f"\n{'=' * 20} SCAN @ {timestamp} {'=' * 20}")

    try:
        ues = requests.get(f"{LOCATION_AF_URL}/location/get-ues").json()
        gnbs = requests.get(f"{LOCATION_AF_URL}/location/get-gnbs").json()
    except Exception as e:
        print(f"❌ API Error: {e}")
        return

    for ue in ues:
        ue_id = ue['ue_id']
        current_lat, current_lng = ue['lat'], ue['lng']
        current_gnb_id = net_mgr.active_connections.get(ue_id)

        print(f"\n🔍 Analyzing UE: {ue_id} (Pos: {current_lat}, {current_lng})")
        print(f"   Currently attached to: {current_gnb_id if current_gnb_id else 'NONE'}")

        best_gnb, best_rsrp = None, -999
        curr_rsrp = -140.0  # Default deep floor

        for gnb in gnbs:
            dist = physics.calculate_distance(current_lat, current_lng, gnb['lat'], gnb['lng'])
            rsrp = physics.calculate_rsrp(dist, gnb['gnb_id'])

            if gnb['gnb_id'] == current_gnb_id:
                curr_rsrp = rsrp

            if dist <= gnb['radius']:
                if rsrp > best_rsrp:
                    best_rsrp = rsrp
                    best_gnb = gnb['gnb_id']
            else:
                print(f"   [Info] {gnb['gnb_id']} ignored (Outside Radius: {dist:.1f}m > {gnb['radius']}m)")

        net_mgr.update_state(ue_id, best_gnb, best_rsrp, curr_rsrp)


if __name__ == "__main__":
    while True:
        orchestrate()
        time.sleep(POLL_INTERVAL)