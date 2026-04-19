import React from 'react';
import { useDroneStore } from '../../store/useDroneStore';
import { BellRing } from 'lucide-react';

const NotificationArea = () => {
  const { messages } = useDroneStore();

  return (
    <div className="absolute bottom-8 right-8 z-[1000] flex flex-col gap-2 pointer-events-none">
      {messages.map((msg, i) => (
        <div 
          key={i} 
          className="bg-white border-l-4 border-blue-500 shadow-xl p-4 rounded-r-lg w-64 animate-in slide-in-from-right duration-300"
        >
          <div className="flex items-center gap-2 mb-1">
            <BellRing size={14} className="text-blue-500" />
            <span className="text-[10px] font-bold uppercase text-slate-400">Network Event</span>
          </div>
          <p className="text-sm text-slate-700 font-medium">{msg}</p>
        </div>
      ))}
    </div>
  );
};

export default NotificationArea;