import React from 'react';
import MapView from './components/Map/MapContainer';
import TelemetryHUD from './components/Overlay/TelemetryHUD';
import AgentTerminal from './components/Overlay/AgentTerminal';
import ControlPanel from './components/Controls/ControlPanel';
import NotificationArea from './components/Overlay/NotificationArea';

// Hooks
import { useNetworkData } from './hooks/useNetworkData';
import { useDronePhysics } from './hooks/useDronePhysics';
import { useKeyboardControls } from './hooks/useKeyboardControls';
import { useWebSocket } from './hooks/useWebSocket';

const App = () => {
  // Initialize all Background Logic
  useNetworkData();      // Data Fetching
  useDronePhysics();     // 60fps Movement & 3s Backend Sync
  useKeyboardControls(); // W/A/S/D Listeners
  useWebSocket();        // Real-time Relay (Handovers/Agent)

  return (
    <div className="w-screen h-screen overflow-hidden bg-slate-50 font-sans antialiased">
      {/* 1. The Map Layer (Bottom) */}
      <MapView />

      {/* 2. HUD Layers (Top/Overlays) */}
      <TelemetryHUD />
      <AgentTerminal />
      
      {/* 3. Interaction Layers */}
      <ControlPanel />
      <NotificationArea />

      {/* Subtle Overlay Vignette for MEC feel */}
      <div className="fixed inset-0 pointer-events-none shadow-[inset_0_0_100px_rgba(0,0,0,0.05)]" />
    </div>
  );
};

export default App;