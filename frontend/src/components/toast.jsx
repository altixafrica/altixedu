import React, { useContext } from 'react';
import { AlertCircle, CheckCircle, InfoIcon, X, AlertTriangle } from 'lucide-react';
import { ToastContext } from '../lib/toast-context';

export const Toast = () => {
  const { toasts, removeToast } = useContext(ToastContext);

  const iconMap = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: InfoIcon,
    default: AlertCircle,
  };

  const colorMap = {
    success: 'bg-green-50 text-green-900 border-green-200',
    error: 'bg-red-50 text-red-900 border-red-200',
    warning: 'bg-yellow-50 text-yellow-900 border-yellow-200',
    info: 'bg-blue-50 text-blue-900 border-blue-200',
    default: 'bg-slate-50 text-slate-900 border-slate-200',
  };

  const iconColorMap = {
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-yellow-600',
    info: 'text-blue-600',
    default: 'text-slate-600',
  };

  return (
    <div
      className="fixed top-4 right-4 z-50 space-y-3 pointer-events-none"
      role="region"
      aria-live="polite"
      aria-label="Notifications"
    >
      {toasts.map((toast) => {
        const IconComponent = iconMap[toast.type] || iconMap.default;
        const colorClass = colorMap[toast.type] || colorMap.default;
        const iconColorClass = iconColorMap[toast.type] || iconColorMap.default;

        return (
          <div
            key={toast.id}
            className={`flex items-start gap-3 rounded-lg border px-4 py-3 shadow-lg pointer-events-auto animate-in slide-in-from-top-2 fade-in ${colorClass}`}
            role="status"
            aria-label={toast.message}
          >
            <IconComponent className={`h-5 w-5 flex-shrink-0 mt-0.5 ${iconColorClass}`} />
            <span className="text-sm font-medium flex-1">{toast.message}</span>
            <button
              onClick={() => removeToast(toast.id)}
              className="flex-shrink-0 rounded hover:bg-black/10 p-1 transition"
              aria-label={`Close notification: ${toast.message}`}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
