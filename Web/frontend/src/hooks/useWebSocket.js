import { useEffect, useRef } from 'react';
import { useDroneStore } from '../store/useDroneStore';

export const useWebSocket = () => {
  const { addMessage, addThought, setWaypoints } = useDroneStore();
  const socketRef = useRef(null);

  useEffect(() => {
    // Prevent multiple connections
    if (socketRef.current) return;

    const socket = new WebSocket('ws://127.0.0.1:8004/ws/notifications');
    socketRef.current = socket;

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
          case 'HANDOVER':
            addMessage(`Handover: ${msg.data.from} ➔ ${msg.data.to}`);
            break;
          case 'AGENT_THOUGHT':
            addThought(msg.data);
            break;
          case 'WAYPOINTS':
            setWaypoints(msg.data);
            addMessage("New path received from Agent");
            break;
        }
      } catch (err) {
        console.error("WS Parse Error", err);
      }
    };

    socket.onopen = () => console.log("Connected to Relay WebSocket");
    socket.onclose = () => {
      console.log("WS Closed");
      socketRef.current = null;
    };

    return () => {
      if (socket.readyState === 1) { // 1 = OPEN
        socket.close();
      }
      socketRef.current = null;
    };
  }, [addMessage, addThought, setWaypoints]);
};