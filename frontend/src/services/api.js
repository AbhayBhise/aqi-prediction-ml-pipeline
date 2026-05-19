import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Axios response interceptor for handling wake-up preheating retries
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;
    
    // Initialize retry count if not present
    config.retry = config.retry || { count: 0 };
    
    const MAX_RETRIES = 5;
    const RETRY_DELAY_BASE = 2000; // Start with 2 seconds

    // Retry if it's a network error (no response) or a 503/504 status (space preheating)
    const shouldRetry = !response || response.status === 503 || response.status === 504;

    if (shouldRetry && config.retry.count < MAX_RETRIES) {
      config.retry.count += 1;
      const delay = RETRY_DELAY_BASE * Math.pow(2, config.retry.count - 1);
      console.warn(`[API Connection] Space is preheating or rate limited. Retrying request (${config.retry.count}/${MAX_RETRIES}) in ${delay}ms...`);
      
      // Wait for the backoff delay
      await new Promise((resolve) => setTimeout(resolve, delay));
      
      // Resend the request
      return api(config);
    }
    
    return Promise.reject(error);
  }
);

export default api;
