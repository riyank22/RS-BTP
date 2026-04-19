import { useEffect, useRef } from 'react';
import { useDroneStore } from '../store/useDroneStore';
import { calculateNewPos, isInsideNetwork } from '../utils/geoHelpers';
import { updateUeLocation } from '../api/endpoints';

export const useDronePhysics = () => {
  const { 
    position, speed, heading, mode, gnbs, droneId, 
    updatePosition, waypoints, setMode 
  } = useDroneStore();
  
  const lastSyncTime = useRef(0);
  const requestRef = useRef();

  const animate = (time) => {
    if (mode === 'idle') return;

    // 1. Calculate movement for this frame (roughly 60fps)
    // Distance = speed * time_delta (using 0.016s as approx frame time)
    const distancePerFrame = speed * 0.0163; 
    
    let nextPos = position;

    if (mode === 'manual') {
      nextPos = calculateNewPos(position, distancePerFrame, heading);
    } else if (mode === 'autopilot' && waypoints.length > 0) {
      // Basic waypoint following logic could be added here
      // For now, move toward waypoints[0]
    }

    // 2. Boundary Check: Stop if leaving gNB coverage
    if (isInsideNetwork(nextPos, gnbs)) {
      updatePosition(nextPos);
    } else {
      console.warn("Drone reached network boundary. Stopping.");
    }

    // 3. Throttled Sync to Backend (Every 3-5 seconds)
    if (time - lastSyncTime.current > 3000) {
      updateUeLocation({
        id: droneId,
        lat: nextPos.lat,
        lng: nextPos.lng
      }).catch(err => console.error("Sync failed", err));
      
      lastSyncTime.current = time;
    }

    requestRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    requestRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(requestRef.current);
  }, [mode, position, speed, heading, gnbs]); 
};