import React from 'react';
import { useDroneStore } from '../../store/useDroneStore';
import { Activity, Signal, Navigation } from 'lucide-react';

const TelemetryHUD = () => {
  const { position, activeUeStats, speed, mode } = useDroneStore();
  
  const pdu = activeUeStats?.pdu_sessions?.[0];

  return (
    <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2 w-64">
      <div className="bg-white/80 backdrop-blur-md border border-slate-200 p-4 rounded-xl shadow-lg">
        <div className="flex items-center gap-2 mb-3 border-b pb-2">
          <Activity size={18} className="text-blue-600" />
          <h2 className="font-bold text-slate-800 uppercase text-xs tracking-wider">Drone Telemetry</h2>
        </div>
        
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500">Status</span>
            <span className={`font-mono font-bold ${mode === 'manual' ? 'text-orange-500' : 'text-green-500'}`}>
              {mode.toUpperCase()}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-slate-500">5G IP</span>
            <span className="font-mono text-slate-700">{pdu?.pdu_address || '0.0.0.0'}</span>
          </div>

          <div className="flex justify-between items-center">
            <div className="flex items-center gap-1 text-slate-500">
              <Signal size={14} /> <span>QoS (5QI)</span>
            </div>
            <span className={`px-2 py-0.5 rounded text-white font-bold ${pdu?.default_5qi < 5 ? 'bg-green-500' : 'bg-blue-500'}`}>
              {pdu?.default_5qi || 'N/A'}
            </span>
          </div>

          <div className="flex flex-col gap-1 pt-2 border-t mt-2">
            <div className="flex items-center gap-1 text-slate-500 text-[10px] uppercase">
              <Navigation size={12} /> <span>Coordinates</span>
            </div>
            <span className="font-mono text-[11px] text-slate-600">
              {position.lat.toFixed(6)}, {position.lng.toFixed(6)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TelemetryHUD;