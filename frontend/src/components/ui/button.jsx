import React from 'react';

export const Button = React.forwardRef((
  {
    className = '',
    variant = 'default',
    size = 'md',
    fullWidth = false,
    as: Component = 'button',
    type,
    ariaLabel,
    ariaPressed,
    ariaExpanded,
    ...props
  },
  ref
) => {
  const baseStyles =
    'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-brand-500/30 disabled:cursor-not-allowed disabled:opacity-50 dark:focus:ring-brand-400/30';
  
  const variants = {
    default: 'bg-brand-600 text-white shadow-sm shadow-brand-900/10 hover:bg-brand-500 dark:bg-brand-700 dark:hover:bg-brand-600',
    primary: 'bg-brand-600 text-white shadow-sm shadow-brand-900/10 hover:bg-brand-500 dark:bg-brand-700 dark:hover:bg-brand-600',
    secondary: 'bg-white text-slate-900 ring-1 ring-inset ring-slate-200 hover:bg-slate-50 dark:bg-slate-800 dark:text-slate-100 dark:ring-slate-700 dark:hover:bg-slate-700',
    outline: 'bg-transparent text-slate-900 ring-1 ring-inset ring-slate-300 hover:bg-slate-100/70 dark:text-slate-100 dark:ring-slate-600 dark:hover:bg-slate-800/70',
    ghost: 'bg-transparent text-slate-700 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-slate-100',
    danger: 'bg-red-600 text-white shadow-lg shadow-red-900/15 hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-600',
  };

  const sizes = {
    sm: 'h-9 px-4 text-sm',
    md: 'h-11 px-5 text-sm',
    lg: 'h-12 px-6 text-base',
    xl: 'h-14 px-8 text-lg',
  };

  const componentProps = {
    className: `${baseStyles} ${variants[variant]} ${sizes[size]} ${fullWidth ? 'w-full' : ''} ${className}`.trim(),
    ref,
    ...(ariaLabel && { 'aria-label': ariaLabel }),
    ...(ariaPressed !== undefined && { 'aria-pressed': ariaPressed }),
    ...(ariaExpanded !== undefined && { 'aria-expanded': ariaExpanded }),
    ...props,
  };

  if (Component === 'button') {
    componentProps.type = type || 'button';
  }

  return (
    <Component {...componentProps} />
  );
});

Button.displayName = 'Button';
