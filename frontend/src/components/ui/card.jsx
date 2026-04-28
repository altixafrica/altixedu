import React from 'react';

export const Card = ({ className = '', ...props }) => (
  <div
    className={`rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-950/[0.03] ${className}`}
    {...props}
  />
);

export const CardHeader = ({ className = '', ...props }) => (
  <div className={`px-6 py-5 ${className}`} {...props} />
);

export const CardTitle = ({ className = '', ...props }) => (
  <h2 className={`text-lg font-semibold text-slate-900 ${className}`} {...props} />
);

export const CardDescription = ({ className = '', ...props }) => (
  <p className={`text-sm text-slate-500 ${className}`} {...props} />
);

export const CardContent = ({ className = '', ...props }) => (
  <div className={`px-6 pb-6 ${className}`} {...props} />
);

export const CardFooter = ({ className = '', ...props }) => (
  <div className={`border-t border-slate-200 px-6 py-4 ${className}`} {...props} />
);
