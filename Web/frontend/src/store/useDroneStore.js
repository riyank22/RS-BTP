import { create } from 'zustand';

export const useDroneStore = create((set) => ({
  // Drone State
  droneId: 'imsi-208930000000001',
  position: { lat: 23.2449, lng: 72.6151 },
  heading: 0,
  speed: 10, // m/s
  mode: 'manual', // 'manual' | 'autopilot' | 'idle'
  trail: [],
  
  // Network Data
  gnbs: [],
  ues: [],
  restrictedAreas: [],
  activeUeStats: null,
  
  // UI State
  messages: [], // Handover/Status notifications
  thoughts: [], // Agent reasoning
  waypoints: [], // Recommended path
  
  // Actions
  updatePosition: (pos) => set((state) => ({ 
    position: pos, 
    trail: [...state.trail.slice(-100), pos] // Keep last 100 points
  })),
  setHeading: (deg) => set({ heading: deg }),
  setSpeed: (s) => set({ speed: s }),
  setMode: (m) => set({ mode: m }),
  setNetworkData: (data) => set({ 
    gnbs: data.gnbs, 
    ues: data.ues, 
    restrictedAreas: data.restricted_areas 
  }),
  setUeStats: (stats) => set({ activeUeStats: stats }),
  addThought: (msg) => set((state) => ({ thoughts: [msg, ...state.thoughts].slice(0, 5) })),
  addMessage: (msg) => set((state) => ({ messages: [msg, ...state.messages].slice(0, 3) })),
  setWaypoints: (pts) => set({ waypoints: pts }),
}));