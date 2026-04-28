/**
 * Page Error Fallback Component
 * Shows when a specific page fails to load (API error, etc.)
 * Different from ErrorBoundary - this is for API/data errors
 */

import React from 'react';
import { AlertCircle, RefreshCw, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';

export const PageErrorFallback = ({
  title = 'Page Error',
  message = 'Failed to load this page. Please try again.',
  error = null,
  onRetry = null,
  showDetails = false,
}) => {
  const navigate = useNavigate();

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      window.location.reload();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-white py-12">
      <div className="container mx-auto px-4 md:px-6">
        <div className="max-w-md mx-auto">
          {/* Error Icon */}
          <div className="flex justify-center mb-6">
            <div className="p-3 bg-red-100 rounded-full">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
          </div>

          {/* Error Message */}
          <h1 className="text-2xl font-bold text-slate-900 text-center mb-2">
            {title}
          </h1>
          <p className="text-slate-600 text-center mb-6">
            {message}
          </p>

          {/* Error Details */}
          {showDetails && error && (
            <div className="mb-6 p-4 bg-slate-100 rounded-lg border border-slate-200">
              <p className="text-xs font-mono text-slate-700 break-words">
                {typeof error === 'string' ? error : error.message || 'Unknown error'}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="space-y-3">
            {onRetry && (
              <Button
                fullWidth
                variant="primary"
                onClick={handleRetry}
                className="flex items-center justify-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Try Again
              </Button>
            )}
            <Button
              fullWidth
              variant="secondary"
              onClick={() => navigate(-1)}
              className="flex items-center justify-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Go Back
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PageErrorFallback;
