import React from 'react';
import { Marker, Polyline, Popup } from 'react-leaflet';
import L from 'leaflet';
import { useDroneStore } from '../../store/useDroneStore';

const DroneMarker = () => {
  const { position, heading, trail, activeUeStats } = useDroneStore();

  // Custom SVG Arrow for the Drone
  const droneIcon = L.divIcon({
    html: `
      <div style="transform: rotate(${heading}deg); transition: transform 0.1s linear;">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L4.5 20.29L5.21 21L12 18L18.79 21L19.5 20.29L12 2Z" fill="#3b82f6" stroke="white" stroke-width="2"/>
        </svg>
      </div>
    `,
    className: 'drone-icon-container',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
  });

  return (
    <>
      {/* Flight Trail */}
      <Polyline 
        positions={trail.map(p => [p.lat, p.lng])} 
        pathOptions={{ color: '#3b82f6', weight: 3, dashArray: '5, 5', opacity: 0.6 }} 
      />
      
      {/* Current Drone Position */}
      <Marker position={[position.lat, position.lng]} icon={droneIcon}>
        {activeUeStats && (
          <Popup>
            <div className="text-xs">
              <p className="font-bold">SUPI: {activeUeStats.supi}</p>
              <p>IP: {activeUeStats.pdu_sessions[0]?.pdu_address}</p>
              <p>5QI: <span className="text-blue-600 font-bold">{activeUeStats.pdu_sessions[0]?.default_5qi}</span></p>
            </div>
          </Popup>
        )}
      </Marker>
    </>
  );
};

export default DroneMarker;