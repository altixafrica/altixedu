import React from 'react';

export const Badge = ({ className = '', variant = 'default', ...props }) => {
  const variants = {
    default: 'bg-slate-100 text-slate-800',
    primary: 'bg-brand-100 text-brand-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-amber-100 text-amber-800',
    error: 'bg-red-100 text-red-800',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${variants[variant]} ${className}`}
      {...props}
    />
  );
};

export const Alert = ({ className = '', variant = 'default', ...props }) => {
  const variants = {
    default: 'bg-slate-50 border-slate-200 text-slate-900',
    info: 'bg-blue-50 border-blue-200 text-blue-900',
    success: 'bg-green-50 border-green-200 text-green-900',
    warning: 'bg-amber-50 border-amber-200 text-amber-900',
    error: 'bg-red-50 border-red-200 text-red-900',
  };

  return (
    <div
      className={`rounded-lg border px-4 py-3 ${variants[variant]} ${className}`}
      {...props}
    />
  );
};
