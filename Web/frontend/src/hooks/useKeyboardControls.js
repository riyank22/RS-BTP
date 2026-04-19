import { useEffect } from 'react';
import { useDroneStore } from '../store/useDroneStore';

export const useKeyboardControls = () => {
  const { heading, setHeading, setMode, mode } = useDroneStore();

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (mode !== 'manual' && mode !== 'idle') return;

      switch (e.key.toLowerCase()) {
        case 'w':
        case 'arrowup':
          setMode('manual');
          break;
        case 'a':
        case 'arrowleft':
          setHeading((heading - 10 + 360) % 360);
          break;
        case 'd':
        case 'arrowright':
          setHeading((heading + 10) % 360);
          break;
        case 's':
        case 'arrowdown':
          // Optional: Reverse or stop
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [heading, mode]);
};