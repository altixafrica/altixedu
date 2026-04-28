/**
 * usePageError Hook
 * Simplified error handling for page components
 * Provides state and error display logic
 */

import { useState, useCallback } from 'react';

export const usePageError = (initialError = null) => {
  const [error, setError] = useState(initialError);
  const [isRetrying, setIsRetrying] = useState(false);

  const setPageError = useCallback((err) => {
    if (err instanceof Error) {
      setError({
        message: err.message,
        category: 'error',
        originalError: err,
      });
    } else if (typeof err === 'string') {
      setError({
        message: err,
        category: 'error',
      });
    } else {
      setError(err);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
    setIsRetrying(false);
  }, []);

  const handleRetry = useCallback(async (retryFn) => {
    clearError();
    setIsRetrying(true);

    try {
      await retryFn();
      setIsRetrying(false);
    } catch (err) {
      setPageError(err);
      setIsRetrying(false);
    }
  }, [clearError, setPageError]);

  return {
    error,
    setError: setPageError,
    clearError,
    handleRetry,
    isRetrying,
    hasError: !!error,
  };
};

export default usePageError;
