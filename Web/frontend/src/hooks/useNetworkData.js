import { useEffect } from 'react';
import { useDroneStore } from '../store/useDroneStore';
import { fetchNetworkDetails, fetchUeStats } from '../api/endpoints';

export const useNetworkData = () => {
  const { droneId, setNetworkData, setUeStats, addMessage } = useDroneStore();

  // 1. Initial Load: Get gNBs and Restricted Areas
  useEffect(() => {
    const initLoad = async () => {
      try {
        const data = await fetchNetworkDetails();
        setNetworkData(data);
        addMessage("Network Topology Loaded");
      } catch (err) {
        console.error("Failed to load network details", err);
      }
    };
    initLoad();
  }, [setNetworkData, addMessage]);

  // 2. Dynamic Polling: Get UE Stats (QoS/IP) every 4 seconds
  useEffect(() => {
    if (!droneId) return;

    const pollStats = async () => {
      try {
        const stats = await fetchUeStats(droneId);
        setUeStats(stats);
      } catch (err) {
        console.warn("Could not fetch UE stats", err);
      }
    };

    const interval = setInterval(pollStats, 4000);
    pollStats(); // Initial call

    return () => clearInterval(interval);
  }, [droneId, setUeStats]);
};