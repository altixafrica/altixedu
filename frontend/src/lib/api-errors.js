/**
 * API Error Handler
 * Centralized error mapping to user-friendly messages
 * Provides consistent error handling across the app
 */

import { log } from './config';

/**
 * Error categories for different types of failures
 */
export const ErrorCategory = {
  VALIDATION: 'validation',
  AUTHENTICATION: 'authentication',
  AUTHORIZATION: 'authorization',
  NOT_FOUND: 'not_found',
  CONFLICT: 'conflict',
  RATE_LIMIT: 'rate_limit',
  SERVER_ERROR: 'server_error',
  NETWORK_ERROR: 'network_error',
  OFFLINE: 'offline',
  TIMEOUT: 'timeout',
  UNKNOWN: 'unknown',
};

/**
 * Detailed error information structure
 */
export class APIError {
  constructor(message, category = ErrorCategory.UNKNOWN, originalError = null, statusCode = null) {
    this.message = message; // User-friendly message
    this.category = category; // Error type
    this.statusCode = statusCode; // HTTP status code
    this.originalError = originalError; // Original error object
    this.timestamp = new Date().toISOString();
  }

  /**
   * Get detailed error info for logging
   */
  toJSON() {
    return {
      message: this.message,
      category: this.category,
      statusCode: this.statusCode,
      timestamp: this.timestamp,
    };
  }
}

/**
 * Map HTTP status codes to user-friendly messages
 */
const statusCodeMessages = {
  400: {
    default: 'Please check your input and try again',
    category: ErrorCategory.VALIDATION,
  },
  401: {
    default: 'Your session has expired. Please log in again',
    category: ErrorCategory.AUTHENTICATION,
  },
  403: {
    default: "You don't have permission to perform this action",
    category: ErrorCategory.AUTHORIZATION,
  },
  404: {
    default: 'The requested resource was not found',
    category: ErrorCategory.NOT_FOUND,
  },
  409: {
    default: 'This resource already exists or there is a conflict',
    category: ErrorCategory.CONFLICT,
  },
  429: {
    default: 'Too many requests. Please wait a moment and try again',
    category: ErrorCategory.RATE_LIMIT,
  },
  500: {
    default: 'Server error. Please try again later',
    category: ErrorCategory.SERVER_ERROR,
  },
  502: {
    default: 'Service temporarily unavailable. Please try again later',
    category: ErrorCategory.SERVER_ERROR,
  },
  503: {
    default: 'Service temporarily unavailable. Please try again later',
    category: ErrorCategory.SERVER_ERROR,
  },
  504: {
    default: 'Request timeout. Please try again later',
    category: ErrorCategory.TIMEOUT,
  },
};

/**
 * Extract user-friendly error message from API response
 */
const extractErrorMessage = (errorResponse) => {
  if (typeof errorResponse === 'string') {
    return errorResponse;
  }

  if (typeof errorResponse === 'object') {
    // Check common error fields
    if (errorResponse.detail) return errorResponse.detail;
    if (errorResponse.error) return errorResponse.error;
    if (errorResponse.message) return errorResponse.message;
    
    // Check for field-level errors
    for (const key in errorResponse) {
      if (Array.isArray(errorResponse[key]) && errorResponse[key].length > 0) {
        return `${key}: ${errorResponse[key][0]}`;
      }
      if (typeof errorResponse[key] === 'string') {
        return errorResponse[key];
      }
    }
  }

  return null;
};

/**
 * Handle API errors and return standardized error object
 * @param {Error} error - Axios error or any error
 * @returns {APIError}
 */
export const handleAPIError = (error) => {
  log.error('Handling API error:', error);

  // Handle offline errors
  if (error.isOffline === true) {
    return new APIError(
      'No internet connection. Please check your network and try again',
      ErrorCategory.OFFLINE,
      error,
      null
    );
  }

  // Handle timeout
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    return new APIError(
      'Request took too long. Please try again',
      ErrorCategory.TIMEOUT,
      error,
      null
    );
  }

  // Handle network errors
  if (!error.response) {
    // Network error (no response from server)
    const message = error.message === 'Network Error'
      ? 'Network error. Please check your connection'
      : error.message || 'An unexpected error occurred';

    return new APIError(
      message,
      ErrorCategory.NETWORK_ERROR,
      error,
      null
    );
  }

  // Handle HTTP error responses
  const statusCode = error.response.status;
  const statusInfo = statusCodeMessages[statusCode] || statusCodeMessages[500];

  // Try to extract specific error message from backend
  const specificMessage = extractErrorMessage(error.response.data);
  const userMessage = specificMessage || statusInfo.default;

  return new APIError(
    userMessage,
    statusInfo.category,
    error,
    statusCode
  );
};

/**
 * Check if error should trigger a retry
 * @param {Error} error - Error object
 * @returns {boolean}
 */
export const shouldRetry = (error) => {
  if (!error.response) {
    // Network errors should be retried
    return true;
  }

  const status = error.response.status;
  // Don't retry client errors (4xx), except for specific cases
  if (status >= 400 && status < 500) {
    return status === 408 || status === 429; // Timeout or Rate limit
  }

  // Retry server errors (5xx)
  return status >= 500;
};

/**
 * Format error for logging/reporting
 * @param {APIError|Error} error
 * @returns {object}
 */
export const formatErrorForLogging = (error) => {
  if (error instanceof APIError) {
    return {
      message: error.message,
      category: error.category,
      statusCode: error.statusCode,
      timestamp: error.timestamp,
      originalError: error.originalError?.message,
    };
  }

  return {
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString(),
  };
};

export default {
  APIError,
  ErrorCategory,
  handleAPIError,
  shouldRetry,
  formatErrorForLogging,
};
