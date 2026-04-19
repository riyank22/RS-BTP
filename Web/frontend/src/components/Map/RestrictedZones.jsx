import React from 'react';
import { Circle, Polygon } from 'react-leaflet';
import { useDroneStore } from '../../store/useDroneStore';

const RestrictedZones = () => {
  const { restrictedAreas } = useDroneStore();

  const getStyle = (type) => ({
    fillColor: type === 'RED' ? '#ef4444' : '#ec4899', // Red vs Pink
    fillOpacity: 0.3,
    color: type === 'RED' ? '#b91c1c' : '#be185d',
    weight: 2,
  });

  return (
    <>
      {restrictedAreas.map((zone) => {
        if (zone.shape === 'CIRCLE') {
          return (
            <Circle
              key={zone.zone_id}
              center={zone.data.center}
              radius={zone.data.radius}
              pathOptions={getStyle(zone.zone_type)}
            />
          );
        }
        if (zone.shape === 'POLYGON') {
          return (
            <Polygon
              key={zone.zone_id}
              positions={zone.data.coords}
              pathOptions={getStyle(zone.zone_type)}
            />
          );
        }
        return null;
      })}
    </>
  );
};

export default RestrictedZones;