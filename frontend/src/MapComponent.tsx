import React from 'react';
import { GoogleMap, useJsApiLoader, Marker } from '@react-google-maps/api';

interface Agent {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
}

interface MapProps {
  agents: Agent[];
}

const containerStyle = {
  width: '100%',
  height: '400px'
};

const center = {
  lat: 0,
  lng: 0
};

const MapComponent: React.FC<MapProps> = ({ agents }) => {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY
  });

  return isLoaded ? (
    <GoogleMap
      mapContainerStyle={containerStyle}
      center={center}
      zoom={2}
    >
      {agents.map(agent => (
        <Marker
          key={agent.id}
          position={{ lat: agent.latitude, lng: agent.longitude }}
          title={agent.name}
        />
      ))}
    </GoogleMap>
  ) : <></>
}

export default React.memo(MapComponent);
