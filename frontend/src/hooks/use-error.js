import { useEffect } from 'react';
import { useError } from '../components/error-display';
import { formatErrorForDisplay } from './error-handler';

/**
 * Hook to automatically display API errors
 * Usage: useApiError(error) where error is from a try-catch or API call
 */
export const useApiError = (error) => {
  const { addError } = useError();

  useEffect(() => {
    if (error) {
      const formatted = formatErrorForDisplay(error);
      addError(formatted.message);
    }
  }, [error, addError]);
};

/**
 * Hook for handling async operations with error display
 * Usage: const { execute, loading, error } = useAsyncError()
 */
export const useAsyncError = () => {
  const { addError } = useError();

  const execute = async (fn) => {
    try {
      return await fn();
    } catch (error) {
      const formatted = formatErrorForDisplay(error);
      addError(formatted.message);
      throw error;
    }
  };

  return { execute, addError };
};

/**
 * Hook for handling form submission errors
 * Returns both message and field-level errors
 */
export const useFormError = () => {
  const { addError } = useError();

  const handleError = (error) => {
    const formatted = formatErrorForDisplay(error);
    if (formatted.isFieldError) {
      // Field-level errors don't need to be displayed as toast
      // They should be shown next to the fields
      return formatted;
    }
    addError(formatted.message);
    return formatted;
  };

  return { handleError, addError };
};
