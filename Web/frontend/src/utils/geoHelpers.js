/**
 * Calculates new Lat/Lng based on distance and bearing
 * @param {Object} start - {lat, lng}
 * @param {number} distance - meters
 * @param {number} bearing - degrees
 */
export const calculateNewPos = (start, distance, bearing) => {
  const R = 6371000; // Earth Radius in meters
  const brng = (bearing * Math.PI) / 180;
  const lat1 = (start.lat * Math.PI) / 180;
  const lon1 = (start.lng * Math.PI) / 180;

  const lat2 = Math.asin(
    Math.sin(lat1) * Math.cos(distance / R) +
      Math.cos(lat1) * Math.sin(distance / R) * Math.cos(brng)
  );

  const lon2 = lon1 + Math.atan2(
    Math.sin(brng) * Math.sin(distance / R) * Math.cos(lat1),
    Math.cos(distance / R) - Math.sin(lat1) * Math.sin(lat2)
  );

  return {
    lat: (lat2 * 180) / Math.PI,
    lng: (lon2 * 180) / Math.PI,
  };
};

/**
 * Checks if a point is within any gNB radius
 */
export const isInsideNetwork = (point, gnbs) => {
  if (gnbs.length === 0) return true; // Initial state
  return gnbs.some(gnb => {
    const dist = getDistance(point, { lat: gnb.lat, lng: gnb.lng });
    return dist <= gnb.radius;
  });
};

const getDistance = (p1, p2) => {
  const R = 6371000;
  const dLat = ((p2.lat - p1.lat) * Math.PI) / 180;
  const dLon = ((p2.lng - p1.lng) * Math.PI) / 180;
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(p1.lat * Math.PI / 180) * Math.cos(p2.lat * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
};