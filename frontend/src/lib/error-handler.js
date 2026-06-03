/**
 * Global error handler with user-friendly messages
 */

const ERROR_MESSAGES = {
  // Network errors
  'Network Error': 'Unable to connect to server. Check your internet connection.',
  'ECONNREFUSED': 'Server is not responding. Please try again in a few moments.',
  'ETIMEDOUT': 'Request timed out. The server took too long to respond.',
  
  // Authentication errors
  401: 'Your session has expired. Please log in again.',
  403: 'You do not have permission to perform this action.',
  
  // Validation errors
  400: 'Invalid data submitted. Please check your inputs.',
  
  // Server errors
  500: 'Server error. Our team has been notified. Please try again later.',
  502: 'Service temporarily unavailable. Please try again soon.',
  503: 'Server maintenance in progress. Please try again later.',
  
  // Not found
  404: 'The requested resource was not found.',
};

const FIELD_ERRORS = {
  'username': 'Username already exists',
  'email': 'Email already in use',
  'subdomain': 'Subdomain already taken',
  'required': 'This field is required',
  'unique': 'This value already exists',
  'invalid': 'Invalid value',
};

export const getErrorMessage = (error) => {
  // Handle null/undefined
  if (!error) {
    return 'An unexpected error occurred. Please try again.';
  }

  // Handle response errors
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    // Check for specific API error message
    if (data?.detail) {
      return data.detail;
    }

    // Check for field-specific errors (form validation)
    if (typeof data === 'object' && !Array.isArray(data)) {
      const fieldError = Object.entries(data).find(([, value]) => {
        return Array.isArray(value) && value.length > 0;
      });
      
      if (fieldError) {
        const [field, errors] = fieldError;
        const error = errors[0];
        if (typeof error === 'string') {
          return error;
        }
        if (error?.message) {
          return error.message;
        }
      }
    }

    // Check for status code match
    if (ERROR_MESSAGES[status]) {
      return ERROR_MESSAGES[status];
    }

    // Generic response error
    return `Server error (${status}). Please try again.`;
  }

  // Handle request errors (network, timeout)
  if (error.request && !error.response) {
    const message = error.message || error.code || 'Network Error';
    return ERROR_MESSAGES[message] || 'Unable to connect to server. Please check your connection.';
  }

  // Handle message-based errors
  if (error.message) {
    return ERROR_MESSAGES[error.message] || error.message;
  }

  // Fallback
  return 'An unexpected error occurred. Please try again.';
};

export const getFieldErrors = (error) => {
  if (!error?.response?.data || typeof error.response.data !== 'object') {
    return {};
  }

  const errors = {};
  const data = error.response.data;

  // Handle DRF error format: { field: ['error message'] }
  Object.entries(data).forEach(([field, messages]) => {
    if (Array.isArray(messages) && messages.length > 0) {
      errors[field] = Array.isArray(messages) ? messages[0] : messages;
    } else if (typeof messages === 'string') {
      errors[field] = messages;
    }
  });

  return errors;
};

export const formatErrorForDisplay = (error) => {
  return {
    message: getErrorMessage(error),
    fields: getFieldErrors(error),
    isFieldError: Object.keys(getFieldErrors(error)).length > 0,
  };
};

export class UserFriendlyError extends Error {
  constructor(userMessage, technicalMessage = null) {
    super(technicalMessage || userMessage);
    this.userMessage = userMessage;
    this.technicalMessage = technicalMessage;
  }
}
