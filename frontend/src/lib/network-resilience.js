/**
 * Network Resilience Utilities
 * Provides retry logic, timeout handling, offline detection, and request deduplication
 */

import { API_CONFIG, log } from './config';

/**
 * Retry wrapper with exponential backoff
 * @param {Function} fn - Async function to retry
 * @param {number} maxAttempts - Maximum retry attempts
 * @param {number} initialDelay - Initial delay in ms
 * @returns {Promise}
 */
export const withRetry = async (fn, maxAttempts = API_CONFIG.retryAttempts, initialDelay = API_CONFIG.retryDelay) => {
  let lastError;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      log.debug(`Attempt ${attempt}/${maxAttempts}:`, fn.toString().substring(0, 50));
      return await fn();
    } catch (error) {
      lastError = error;
      const status = error.response?.status;
      const shouldRetry = API_CONFIG.retryStatusCodes.includes(status) ||
                          error.code === 'ECONNABORTED' ||
                          error.code === 'ENOTFOUND' ||
                          error.code === 'ECONNREFUSED';
      
      if (!shouldRetry || attempt === maxAttempts) {
        log.warn(`Request failed after ${attempt} attempts:`, error.message);
        throw error;
      }
      
      // Exponential backoff: delay increases with each retry
      const delay = initialDelay * Math.pow(2, attempt - 1);
      log.debug(`Retrying after ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
};

/**
 * Timeout wrapper - rejects promise if it takes too long
 * @param {Promise} promise - Promise to wrap
 * @param {number} ms - Timeout in milliseconds
 * @returns {Promise}
 */
export const withTimeout = (promise, ms = API_CONFIG.timeout) => {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(
        () => reject(new Error(`Request timeout after ${ms}ms`)),
        ms
      )
    ),
  ]);
};

/**
 * Check if browser is online
 * @returns {boolean}
 */
export const isOnline = () => {
  return typeof navigator !== 'undefined' && navigator.onLine;
};

/**
 * Wait for online status
 * @returns {Promise}
 */
export const waitForOnline = () => {
  if (isOnline()) {
    return Promise.resolve();
  }
  
  return new Promise((resolve) => {
    const handleOnline = () => {
      window.removeEventListener('online', handleOnline);
      log.info('Browser came online');
      resolve();
    };
    window.addEventListener('online', handleOnline);
  });
};

/**
 * Request deduplication cache
 * Prevents duplicate requests for the same endpoint
 */
class RequestDeduplicator {
  constructor() {
    this.cache = new Map();
  }

  /**
   * Get or create request promise
   * @param {string} key - Unique cache key
   * @param {Function} fn - Function that returns the request promise
   * @returns {Promise}
   */
  async execute(key, fn) {
    // Return cached promise if exists
    if (this.cache.has(key)) {
      log.debug('Request cache hit:', key);
      return this.cache.get(key);
    }

    // Create and cache new promise
    const promise = fn()
      .then(result => {
        // Clear cache after short delay to allow for re-fetches
        setTimeout(() => this.cache.delete(key), 1000);
        return result;
      })
      .catch(error => {
        // Clear cache immediately on error to allow retry
        this.cache.delete(key);
        throw error;
      });

    this.cache.set(key, promise);
    return promise;
  }

  /**
   * Clear specific or all cached requests
   * @param {string} key - Optional key to clear (if omitted, clears all)
   */
  clear(key) {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }

  /**
   * Get cache size
   */
  size() {
    return this.cache.size;
  }
}

export const requestDeduplicator = new RequestDeduplicator();

/**
 * Generate cache key for request
 * @param {string} method - HTTP method
 * @param {string} url - Request URL
 * @param {object} config - Request config (query params, body, etc.)
 * @returns {string}
 */
export const generateCacheKey = (method, url, config = {}) => {
  const queryString = new URLSearchParams(config.params || {}).toString();
  const key = `${method}:${url}${queryString ? '?' + queryString : ''}`;
  return key;
};

export default {
  withRetry,
  withTimeout,
  isOnline,
  waitForOnline,
  requestDeduplicator,
  generateCacheKey,
};
