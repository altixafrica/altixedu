import React from 'react';

export const Card = ({ className = '', ...props }) => (
  <div
    className={`rounded-lg border border-slate-200 bg-white shadow-sm shadow-slate-950/[0.02] dark:border-slate-700 dark:bg-slate-800 dark:shadow-slate-950/20 ${className}`}
    {...props}
  />
);

export const CardHeader = ({ className = '', ...props }) => (
  <div className={`px-5 py-4 ${className}`} {...props} />
);

export const CardTitle = ({ className = '', ...props }) => (
  <h2 className={`text-lg font-semibold text-slate-900 dark:text-white ${className}`} {...props} />
);

export const CardDescription = ({ className = '', ...props }) => (
  <p className={`text-sm text-slate-500 dark:text-slate-400 ${className}`} {...props} />
);

export const CardContent = ({ className = '', ...props }) => (
  <div className={`px-5 pb-5 ${className}`} {...props} />
);

export const CardFooter = ({ className = '', ...props }) => (
  <div className={`border-t border-slate-200 px-6 py-4 dark:border-slate-700 ${className}`} {...props} />
);
