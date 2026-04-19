const BASE_URL = 'http://127.0.0.1:8004/api';

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'API Error' }));
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }
  return response.json();
};

export const fetchNetworkDetails = () => 
  fetch(`${BASE_URL}/network-details`).then(handleResponse);

export const fetchUeStats = (supi) => 
  fetch(`${BASE_URL}/ue-stats/${supi}`).then(handleResponse);

export const updateUeLocation = (payload) => 
  fetch(`${BASE_URL}/update-location`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(handleResponse);

export const getRecommendedPath = (start, end) => {
  const params = new URLSearchParams({
    start_lat: start.lat,
    start_lng: start.lng,
    end_lat: end.lat,
    end_lng: end.lng
  });
  return fetch(`${BASE_URL}/get-recommended-path?${params}`).then(handleResponse);
};