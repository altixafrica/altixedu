import React, { useState, useCallback } from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { Input, Select, Textarea } from './form';

/**
 * FormField Component - Accessible form field with validation, error display, and ARIA labels
 * Features:
 * - Real-time validation with visual feedback
 * - WCAG 2.1 AA compliant
 * - Error message display
 * - Success state indication
 * - Helper text support
 */
export const FormField = React.forwardRef(({
  label,
  name,
  type = 'text',
  error = '',
  success = false,
  helperText = '',
  required = false,
  disabled = false,
  onChange,
  onBlur,
  validator,
  value,
  className = '',
  ...props
}, ref) => {
  const [isTouched, setIsTouched] = useState(false);
  const [internalError, setInternalError] = useState('');
  const fieldId = `field-${name}`;
  const errorId = `${fieldId}-error`;
  const helperId = `${fieldId}-helper`;

  // Real-time validation
  const handleChange = useCallback((e) => {
    const newValue = e.target.value;
    
    if (validator && isTouched) {
      const validationError = validator(newValue);
      setInternalError(validationError || '');
    }

    onChange?.(e);
  }, [validator, isTouched, onChange]);

  const handleBlur = (e) => {
    setIsTouched(true);
    
    if (validator) {
      const validationError = validator(e.target.value);
      setInternalError(validationError || '');
    }

    onBlur?.(e);
  };

  const displayError = error || internalError;
  const showError = displayError && (isTouched || error);

  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label
          htmlFor={fieldId}
          className="text-sm font-medium text-slate-700"
        >
          {label}
          {required && <span className="ml-1 text-red-500" aria-label="required">*</span>}
        </label>
      )}

      <div className="relative">
        <Input
          ref={ref}
          id={fieldId}
          name={name}
          type={type}
          value={value}
          disabled={disabled}
          onChange={handleChange}
          onBlur={handleBlur}
          aria-label={label || name}
          aria-required={required}
          aria-invalid={showError}
          aria-describedby={showError ? errorId : helperText ? helperId : undefined}
          className={`
            transition-colors
            ${showError ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
            ${success && isTouched ? 'border-green-500 focus:border-green-500 focus:ring-green-500/20' : ''}
          `}
          {...props}
        />

        {showError && (
          <AlertCircle
            className="absolute right-3 top-1/2 -translate-y-1/2 text-red-500"
            size={18}
            aria-hidden="true"
          />
        )}

        {success && isTouched && !showError && (
          <CheckCircle
            className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500"
            size={18}
            aria-hidden="true"
          />
        )}
      </div>

      {showError && (
        <p id={errorId} className="text-sm text-red-500 flex items-center gap-1">
          {displayError}
        </p>
      )}

      {helperText && !showError && (
        <p id={helperId} className="text-sm text-slate-500">
          {helperText}
        </p>
      )}
    </div>
  );
});

FormField.displayName = 'FormField';

/**
 * SelectField Component - Accessible select with validation
 */
export const SelectField = React.forwardRef(({
  label,
  name,
  options = [],
  error = '',
  success = false,
  helperText = '',
  required = false,
  disabled = false,
  onChange,
  onBlur,
  value,
  className = '',
  ...props
}, ref) => {
  const [isTouched, setIsTouched] = useState(false);
  const fieldId = `select-${name}`;
  const errorId = `${fieldId}-error`;
  const helperId = `${fieldId}-helper`;

  const handleBlur = (e) => {
    setIsTouched(true);
    onBlur?.(e);
  };

  const showError = error && (isTouched || error);

  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label
          htmlFor={fieldId}
          className="text-sm font-medium text-slate-700"
        >
          {label}
          {required && <span className="ml-1 text-red-500" aria-label="required">*</span>}
        </label>
      )}

      <Select
        ref={ref}
        id={fieldId}
        name={name}
        value={value}
        disabled={disabled}
        onChange={onChange}
        onBlur={handleBlur}
        aria-label={label || name}
        aria-required={required}
        aria-invalid={showError}
        aria-describedby={showError ? errorId : helperText ? helperId : undefined}
        className={`
          transition-colors
          ${showError ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
          ${success && isTouched ? 'border-green-500 focus:border-green-500 focus:ring-green-500/20' : ''}
        `}
        {...props}
      >
        <option value="">Select an option</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>

      {showError && (
        <p id={errorId} className="text-sm text-red-500">
          {error}
        </p>
      )}

      {helperText && !showError && (
        <p id={helperId} className="text-sm text-slate-500">
          {helperText}
        </p>
      )}
    </div>
  );
});

SelectField.displayName = 'SelectField';

/**
 * TextareaField Component - Accessible textarea with validation
 */
export const TextareaField = React.forwardRef(({
  label,
  name,
  error = '',
  success = false,
  helperText = '',
  required = false,
  disabled = false,
  onChange,
  onBlur,
  value,
  className = '',
  ...props
}, ref) => {
  const [isTouched, setIsTouched] = useState(false);
  const fieldId = `textarea-${name}`;
  const errorId = `${fieldId}-error`;
  const helperId = `${fieldId}-helper`;

  const handleBlur = (e) => {
    setIsTouched(true);
    onBlur?.(e);
  };

  const showError = error && (isTouched || error);

  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label
          htmlFor={fieldId}
          className="text-sm font-medium text-slate-700"
        >
          {label}
          {required && <span className="ml-1 text-red-500" aria-label="required">*</span>}
        </label>
      )}

      <Textarea
        ref={ref}
        id={fieldId}
        name={name}
        value={value}
        disabled={disabled}
        onChange={onChange}
        onBlur={handleBlur}
        aria-label={label || name}
        aria-required={required}
        aria-invalid={showError}
        aria-describedby={showError ? errorId : helperText ? helperId : undefined}
        className={`
          transition-colors
          ${showError ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
          ${success && isTouched ? 'border-green-500 focus:border-green-500 focus:ring-green-500/20' : ''}
        `}
        {...props}
      />

      {showError && (
        <p id={errorId} className="text-sm text-red-500">
          {error}
        </p>
      )}

      {helperText && !showError && (
        <p id={helperId} className="text-sm text-slate-500">
          {helperText}
        </p>
      )}
    </div>
  );
});

TextareaField.displayName = 'TextareaField';
