/**
 * Centralized Configuration
 * Loads from environment variables (Vite's import.meta.env)
 * Provides defaults for development
 */

// API Configuration
export const API_CONFIG = {
  // Base URL for all API requests
  url: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // Request timeout in milliseconds
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000', 10),
  
  // Retry configuration
  retryAttempts: parseInt(import.meta.env.VITE_RETRY_ATTEMPTS || '3', 10),
  retryDelay: parseInt(import.meta.env.VITE_RETRY_DELAY || '500', 10),
  
  // HTTP methods to retry (only idempotent methods)
  retryMethods: ['GET', 'HEAD', 'OPTIONS', 'PUT'],
  
  // Status codes to retry on
  retryStatusCodes: [408, 429, 500, 502, 503, 504],
};

// App Configuration
export const APP_CONFIG = {
  environment: import.meta.env.VITE_ENVIRONMENT || 'development',
  isDevelopment: import.meta.env.MODE === 'development',
  isProduction: import.meta.env.MODE === 'production',
  isStaging: import.meta.env.MODE === 'staging',
  
  // Logging
  enableConsoleLogs: import.meta.env.VITE_ENABLE_CONSOLE_LOGS === 'true',
  enableErrorReporting: import.meta.env.VITE_ENABLE_ERROR_REPORTING === 'true',
};

// Authentication Configuration
export const AUTH_CONFIG = {
  tokenKey: 'auth_token',
  sessionKey: 'auth_session',
  userKey: 'user',
  tokenRefreshEndpoint: '/api/auth/token/refresh/',
  loginEndpoint: '/login',
};

// Toast Configuration
export const TOAST_CONFIG = {
  defaultDuration: 3000, // milliseconds
  errorDuration: 5000,
  successDuration: 3000,
  warningDuration: 4000,
  infoDuration: 3000,
};

// Pagination Configuration
export const PAGINATION_CONFIG = {
  defaultPageSize: 10,
  maxPageSize: 100,
};

// Features (can be toggled per environment)
export const FEATURES = {
  enableRealTimeUpdates: false, // WebSocket support (future)
  enableDarkMode: false,
  enableAnalytics: import.meta.env.VITE_ENABLE_ERROR_REPORTING === 'true',
};

// Logging utility
export const log = {
  debug: (...args) => {
    if (APP_CONFIG.enableConsoleLogs && APP_CONFIG.isDevelopment) {
      console.debug('[DEBUG]', ...args);
    }
  },
  
  info: (...args) => {
    if (APP_CONFIG.enableConsoleLogs) {
      console.log('[INFO]', ...args);
    }
  },
  
  warn: (...args) => {
    console.warn('[WARN]', ...args);
  },
  
  error: (...args) => {
    console.error('[ERROR]', ...args);
    
    // Could send to error reporting service
    if (APP_CONFIG.enableErrorReporting && APP_CONFIG.isProduction) {
      // sendToErrorReportingService(args);
    }
  },
};

// Export all as default
export default {
  API_CONFIG,
  APP_CONFIG,
  AUTH_CONFIG,
  TOAST_CONFIG,
  PAGINATION_CONFIG,
  FEATURES,
  log,
};
