import React, { useEffect, useRef } from 'react';
import { useDroneStore } from '../../store/useDroneStore';
import { BrainCircuit } from 'lucide-react';

const AgentTerminal = () => {
  const { thoughts } = useDroneStore();
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0; // Recent thoughts at the top
    }
  }, [thoughts]);

  return (
    <div className="absolute top-4 right-4 z-[1000] w-72">
      <div className="bg-slate-900/95 border border-slate-700 rounded-xl shadow-2xl overflow-hidden">
        <div className="bg-slate-800 px-3 py-2 flex items-center gap-2 border-b border-slate-700">
          <BrainCircuit size={16} className="text-purple-400" />
          <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Agent Reasoning</span>
        </div>
        
        <div 
          ref={scrollRef}
          className="p-3 h-48 overflow-y-auto font-mono text-[11px] space-y-2 flex flex-col"
        >
          {thoughts.length === 0 && (
            <div className="text-slate-600 italic">Awaiting intent...</div>
          )}
          {thoughts.map((thought, i) => (
            <div key={i} className="text-purple-300 border-l-2 border-purple-500/50 pl-2 py-1 bg-purple-500/5">
              <span className="text-purple-500 mr-1 font-bold">{`>`}</span>
              {thought}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AgentTerminal;