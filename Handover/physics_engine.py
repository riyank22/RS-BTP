import math

class PhysicsEngine:
    def __init__(self, p_tx=20.0, l0=40.0, n_exponent=3.0):
        self.p_tx = p_tx
        self.l0 = l0
        self.n_exponent = n_exponent

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        dist = 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return dist

    def calculate_rsrp(self, distance, gnb_id):
        """Calculates RSRP with internal logging of the decay."""
        if distance < 1: distance = 1
        path_loss = self.l0 + 10 * self.n_exponent * math.log10(distance)
        rsrp = self.p_tx - path_loss

        # Verbose Logging for the Physics level
        print(f"   [Physics] {gnb_id}: Dist={distance:.1f}m | PathLoss={path_loss:.1f}dB | RSRP={rsrp:.2f}dBm")
        return rsrp