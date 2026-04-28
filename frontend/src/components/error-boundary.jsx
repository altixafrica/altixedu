/**
 * Global Error Boundary
 * Catches React component errors and prevents app crashes
 * Displays a user-friendly error UI with recovery options
 */

import React from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';
import { log, APP_CONFIG } from '../lib/config';
import { formatErrorForLogging } from '../lib/api-errors';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Update state
    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1,
    }));

    // Log error
    log.error('Error caught by boundary:', {
      message: error.toString(),
      stack: errorInfo.componentStack,
      count: this.state.errorCount + 1,
    });

    // Format and log for analysis
    const formattedError = formatErrorForLogging(error);
    if (APP_CONFIG.enableErrorReporting) {
      // Could send to error reporting service
      console.error('Formatted error for reporting:', formattedError);
    }
  }

  handleReset = () => {
    log.info('User clicked reset button');
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = () => {
    log.info('User clicked reload button');
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-white flex items-center justify-center px-4">
          <div className="max-w-md w-full">
            {/* Error Icon */}
            <div className="flex justify-center mb-6">
              <div className="p-3 bg-red-100 rounded-full">
                <AlertCircle className="h-8 w-8 text-red-600" />
              </div>
            </div>

            {/* Error Message */}
            <h1 className="text-2xl font-bold text-slate-900 text-center mb-2">
              Something went wrong
            </h1>
            <p className="text-slate-600 text-center mb-6">
              We encountered an unexpected error. Please try refreshing the page or contact support if the problem persists.
            </p>

            {/* Error Details (Development Only) */}
            {APP_CONFIG.isDevelopment && this.state.error && (
              <div className="mb-6 p-4 bg-slate-100 rounded-lg border border-slate-200">
                <p className="text-xs font-mono text-slate-700 mb-2 font-semibold">Error Details:</p>
                <p className="text-xs font-mono text-slate-600 mb-3 break-words">
                  {this.state.error.toString()}
                </p>
                {this.state.errorInfo && (
                  <details className="text-xs">
                    <summary className="cursor-pointer text-slate-600 hover:text-slate-800 font-semibold">
                      Component Stack
                    </summary>
                    <pre className="mt-2 text-slate-600 overflow-auto max-h-40 p-2 bg-white rounded border border-slate-200">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            )}

            {/* Error Count Warning */}
            {this.state.errorCount > 3 && (
              <div className="mb-6 p-4 bg-yellow-100 rounded-lg border border-yellow-200">
                <p className="text-sm text-yellow-800">
                  Multiple errors detected ({this.state.errorCount}). There may be a serious issue.
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={this.handleReset}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-700 transition font-medium"
              >
                <RefreshCw className="h-4 w-4" />
                Try Again
              </button>
              <button
                onClick={this.handleReload}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-slate-200 text-slate-900 rounded-lg hover:bg-slate-300 transition font-medium"
              >
                <Home className="h-4 w-4" />
                Go Home
              </button>
            </div>

            {/* Support Link */}
            <p className="text-center text-xs text-slate-500 mt-6">
              Need help?{' '}
              <a href="mailto:support@altixedu.com" className="text-primary hover:underline">
                Contact Support
              </a>
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
