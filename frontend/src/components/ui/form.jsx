import React from 'react';

export const Input = React.forwardRef((
  { className = '', ...props },
  ref
) => (
  <input
    ref={ref}
    className={`flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-base placeholder:text-slate-400 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500 dark:border-slate-600 dark:bg-slate-900 dark:text-white dark:placeholder:text-slate-500 dark:focus:border-brand-500 dark:focus:ring-brand-500/20 dark:disabled:bg-slate-800 ${className}`}
    {...props}
  />
));

Input.displayName = 'Input';

export const Select = React.forwardRef((
  { className = '', ...props },
  ref
) => (
  <select
    ref={ref}
    className={`flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-base focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500 dark:border-slate-600 dark:bg-slate-900 dark:text-white dark:focus:border-brand-500 dark:focus:ring-brand-500/20 dark:disabled:bg-slate-800 ${className}`}
    {...props}
  />
));

Select.displayName = 'Select';

export const Textarea = React.forwardRef((
  { className = '', ...props },
  ref
) => (
  <textarea
    ref={ref}
    className={`flex min-h-[80px] w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-base placeholder:text-slate-400 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500 dark:border-slate-600 dark:bg-slate-900 dark:text-white dark:placeholder:text-slate-500 dark:focus:border-brand-500 dark:focus:ring-brand-500/20 dark:disabled:bg-slate-800 ${className}`}
    {...props}
  />
));

Textarea.displayName = 'Textarea';
