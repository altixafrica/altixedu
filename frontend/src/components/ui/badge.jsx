import React from 'react';

export const Badge = ({ className = '', variant = 'default', ...props }) => {
  const variants = {
    default: 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-100',
    primary: 'bg-brand-100 text-brand-800 dark:bg-brand-900 dark:text-brand-100',
    success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
    warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-100',
    error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
  };

  return (
    <span
      className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-medium ${variants[variant]} ${className}`}
      {...props}
    />
  );
};

export const Alert = ({ className = '', variant = 'default', ...props }) => {
  const variants = {
    default: 'bg-slate-50 border-slate-200 text-slate-900 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-100',
    info: 'bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-900 dark:border-blue-700 dark:text-blue-100',
    success: 'bg-green-50 border-green-200 text-green-900 dark:bg-green-900 dark:border-green-700 dark:text-green-100',
    warning: 'bg-amber-50 border-amber-200 text-amber-900 dark:bg-amber-900 dark:border-amber-700 dark:text-amber-100',
    error: 'bg-red-50 border-red-200 text-red-900 dark:bg-red-900 dark:border-red-700 dark:text-red-100',
  };

  return (
    <div
      className={`rounded-lg border px-4 py-3 ${variants[variant]} ${className}`}
      {...props}
    />
  );
};
