import React, { useState } from 'react';
import { Check, AlertCircle } from 'lucide-react';

/**
 * ValidatedInput - Input with real-time validation feedback
 * Shows success checkmark when valid, error shake on invalid
 * 
 * Usage:
 * <ValidatedInput
 *   value={email}
 *   onChange={setEmail}
 *   validator={(val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)}
 *   placeholder="your@email.com"
 *   label="Email"
 * />
 */
export const ValidatedInput = React.forwardRef((
  {
    value,
    onChange,
    validator,
    className = '',
    label,
    error,
    ...props
  },
  ref
) => {
  const [touched, setTouched] = useState(false);
  const [shake, setShake] = useState(false);
  
  const isValid = validator ? validator(value) : value.length > 0;
  const showValidation = touched && value.length > 0;
  const hasError = showValidation && !isValid;

  const handleBlur = (e) => {
    setTouched(true);
    if (props.onBlur) props.onBlur(e);
  };

  const handleChange = (e) => {
    onChange(e.target.value);
    if (error && !isValid) {
      setShake(true);
      setTimeout(() => setShake(false), 500);
    }
  };

  return (
    <div className="relative">
      {label && (
        <label className="mb-2 block text-sm font-medium text-slate-900">
          {label}
        </label>
      )}
      <div className={`relative ${shake ? 'animate-shake' : ''}`}>
        <input
          ref={ref}
          value={value}
          onChange={handleChange}
          onBlur={handleBlur}
          className={`
            flex h-10 w-full rounded-md border bg-white px-3 py-2 text-base
            placeholder:text-slate-400 focus:outline-none focus:ring-2
            disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500
            transition-all duration-200
            ${hasError 
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
              : showValidation && isValid
              ? 'border-green-300 focus:border-green-500 focus:ring-green-500/20'
              : 'border-slate-300 focus:border-brand-600 focus:ring-brand-600/20'
            }
            ${className}
          `}
          {...props}
        />
        
        {showValidation && (
          isValid ? (
            <Check className="absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-green-500 animate-pulse" />
          ) : (
            <AlertCircle className="absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-red-500 animate-bounce" />
          )
        )}
      </div>
      
      {hasError && error && (
        <p className="mt-1 text-xs text-red-600 animate-pulse">{error}</p>
      )}
    </div>
  );
});

ValidatedInput.displayName = 'ValidatedInput';
