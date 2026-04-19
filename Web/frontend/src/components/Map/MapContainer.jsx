import React, { useEffect } from 'react';
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useDroneStore } from '../../store/useDroneStore';
import GnbLayers from './GnbLayers';
import RestrictedZones from './RestrictedZones';
import DroneMarker from './DroneMarker';

// Component to handle map clicks for drone initiation
const MapEvents = () => {
  const { updatePosition, setMode, gnbs } = useDroneStore();
  
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      // You can add logic here to check if click is within network range
      // before initiating the drone as per your requirement
      updatePosition({ lat, lng });
      setMode('manual');
      console.log(`Drone initiated at: ${lat}, ${lng}`);
    },
  });
  return null;
};

const MapView = () => {
  const { gnbs } = useDroneStore();

  return (
    <div className="h-screen w-full relative">
      <MapContainer
        center={[23.245, 72.61]} // Centered on Gandhinagar/Campus
        zoom={15}
        className="h-full w-full"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        
        <MapEvents />
        <GnbLayers />
        <RestrictedZones />
        <DroneMarker />
      </MapContainer>
    </div>
  );
};

export default MapView;