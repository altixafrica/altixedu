import React, { createContext, useState, useCallback } from 'react';
import { AlertCircle, X } from 'lucide-react';

export const ErrorContext = createContext();

export const ErrorProvider = ({ children }) => {
  const [errors, setErrors] = useState([]);

  const addError = useCallback((message, duration = 5000) => {
    const id = Date.now();
    const error = { id, message };
    
    setErrors((prev) => [...prev, error]);

    if (duration) {
      setTimeout(() => {
        removeError(id);
      }, duration);
    }

    return id;
  }, []);

  const removeError = useCallback((id) => {
    setErrors((prev) => prev.filter((e) => e.id !== id));
  }, []);

  const clearAllErrors = useCallback(() => {
    setErrors([]);
  }, []);

  return (
    <ErrorContext.Provider value={{ errors, addError, removeError, clearAllErrors }}>
      {children}
      <ErrorDisplay errors={errors} onRemove={removeError} />
    </ErrorContext.Provider>
  );
};

export const useError = () => {
  const context = React.useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within ErrorProvider');
  }
  return context;
};

const ErrorDisplay = ({ errors, onRemove }) => {
  if (errors.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      {errors.map((error) => (
        <div
          key={error.id}
          className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3 shadow-lg animate-slide-in"
        >
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-red-800 text-sm font-medium line-clamp-3">
              {error.message}
            </p>
          </div>
          <button
            onClick={() => onRemove(error.id)}
            className="text-red-400 hover:text-red-600 flex-shrink-0 ml-2"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      ))}
    </div>
  );
};

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="w-6 h-6 text-red-600" />
              <h1 className="text-xl font-bold text-gray-900">
                Something went wrong
              </h1>
            </div>
            <p className="text-gray-600 text-sm mb-6">
              {this.state.error?.message || 'An unexpected error occurred'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.href = '/';
              }}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition-colors"
            >
              Go to Home
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
