import React from 'react';
import { Circle, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { useDroneStore } from '../../store/useDroneStore';

// Custom Tower Icon
const towerIcon = new L.Icon({
  iconUrl: 'https://cdn-icons-png.flaticon.com/512/5753/5753903.png',
  iconSize: [30, 30],
  iconAnchor: [15, 30],
});

const GnbLayers = () => {
  const { gnbs } = useDroneStore();

  // Distinct colors for MEC style
  const colors = ['#8b5cf6', '#f59e0b', '#10b981', '#3b82f6'];

  return (
    <>
      {gnbs.map((gnb, index) => (
        <React.Fragment key={gnb.gnb_id}>
          {/* Coverage Circle */}
          <Circle
            center={[gnb.lat, gnb.lng]}
            radius={gnb.radius}
            pathOptions={{
              fillColor: colors[index % colors.length],
              fillOpacity: 0.15,
              color: colors[index % colors.length],
              weight: 2,
              dashArray: '5, 10',
            }}
          />
          {/* Tower Marker */}
          <Marker position={[gnb.lat, gnb.lng]} icon={towerIcon}>
            <Popup>
              <div className="font-sans text-xs">
                <p className="font-bold border-b mb-1">{gnb.name}</p>
                <p>ID: {gnb.gnb_id}</p>
                <p>Connected UEs: {gnb.ue_count}</p>
                <p>IP: {gnb.n2_ip}</p>
              </div>
            </Popup>
          </Marker>
        </React.Fragment>
      ))}
    </>
  );
};

export default GnbLayers;