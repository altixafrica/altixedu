// API client using axios
import axios from 'axios';
import { API_CONFIG, AUTH_CONFIG, log } from './config';
import { withRetry, withTimeout, isOnline, waitForOnline } from './network-resilience';

export const apiClient = axios.create({
  baseURL: API_CONFIG.url,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(AUTH_CONFIG.tokenKey);
  if (token) {
    config.headers.Authorization = `Token ${token}`;
    log.debug('Added auth token to request:', config.url);
  }
  return config;
});

// Handle response errors with proper logging and offline detection
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status;
    
    // Log detailed error information
    log.error('API Error:', {
      status,
      url: error.config?.url,
      message: error.message,
      data: error.response?.data,
    });

    // Handle 401 Unauthorized - session expired
    if (status === 401) {
      log.warn('Unauthorized (401) - clearing session and redirecting to login');
      localStorage.removeItem(AUTH_CONFIG.tokenKey);
      localStorage.removeItem(AUTH_CONFIG.userKey);
      localStorage.removeItem(AUTH_CONFIG.sessionKey);
      window.location.href = AUTH_CONFIG.loginEndpoint;
      return Promise.reject(error);
    }

    // Handle offline status
    if (!isOnline()) {
      log.warn('Request failed - browser appears to be offline');
      error.isOffline = true;
      return Promise.reject(error);
    }

    // Retry logic is handled at the api-service.js level
    return Promise.reject(error);
  }
);

export default apiClient;
