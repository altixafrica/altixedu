import React from 'react';

// Form validation utilities
export const validators = {
  // Email validation
  email: (value) => {
    if (!value) return 'Email is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) return 'Please enter a valid email address';
    return '';
  },

  // Required field validation
  required: (value, fieldName = 'This field') => {
    if (!value || value.trim() === '') {
      return `${fieldName} is required`;
    }
    return '';
  },

  // Username validation (alphanumeric + underscore, 3-20 chars)
  username: (value) => {
    if (!value) return 'Username is required';
    if (value.length < 3) return 'Username must be at least 3 characters';
    if (value.length > 20) return 'Username must be at most 20 characters';
    if (!/^[a-zA-Z0-9_]+$/.test(value)) {
      return 'Username can only contain letters, numbers, and underscores';
    }
    return '';
  },

  // Password validation (min 6 chars, at least 1 uppercase, 1 number)
  password: (value) => {
    if (!value) return 'Password is required';
    if (value.length < 6) return 'Password must be at least 6 characters';
    if (!/[A-Z]/.test(value)) return 'Password must contain at least one uppercase letter';
    if (!/[0-9]/.test(value)) return 'Password must contain at least one number';
    return '';
  },

  // Phone validation (Nigerian format or international)
  phone: (value) => {
    if (!value) return '';
    const phoneRegex = /^(?:\+234|0)[0-9]{10}$/;
    if (!phoneRegex.test(value.replace(/\s/g, ''))) {
      return 'Please enter a valid phone number';
    }
    return '';
  },

  // URL validation
  url: (value) => {
    if (!value) return '';
    try {
      new URL(value);
      return '';
    } catch {
      return 'Please enter a valid URL';
    }
  },

  // Hex color validation
  hexColor: (value) => {
    if (!value) return '';
    if (!/^#[0-9A-F]{6}$/i.test(value)) {
      return 'Please enter a valid hex color (e.g., #0f172a)';
    }
    return '';
  },

  // Classroom format (e.g., "SS 3A")
  classroom: (value) => {
    if (!value) return 'Classroom is required';
    if (!/^[A-Z]{1,3}\s[0-9]{1,2}[A-Z]?$/i.test(value)) {
      return 'Please enter a valid classroom (e.g., SS 3A)';
    }
    return '';
  },

  // Admission number format
  admissionNumber: (value) => {
    if (!value) return 'Admission number is required';
    if (!/^[0-9]{6,8}$/.test(value)) {
      return 'Admission number must be 6-8 digits';
    }
    return '';
  },

  // Min length validation
  minLength: (value, minLength, fieldName = 'This field') => {
    if (!value) return `${fieldName} is required`;
    if (value.length < minLength) {
      return `${fieldName} must be at least ${minLength} characters`;
    }
    return '';
  },

  // Max length validation
  maxLength: (value, maxLength, fieldName = 'This field') => {
    if (value && value.length > maxLength) {
      return `${fieldName} must not exceed ${maxLength} characters`;
    }
    return '';
  },

  // File size validation (in MB)
  fileSize: (file, maxSizeMB) => {
    if (!file) return '';
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return `File size must not exceed ${maxSizeMB}MB`;
    }
    return '';
  },

  // File type validation
  fileType: (file, allowedTypes) => {
    if (!file) return '';
    if (!allowedTypes.includes(file.type)) {
      return `File type must be one of: ${allowedTypes.join(', ')}`;
    }
    return '';
  },
};

// Form error state handler
export const useFormErrors = (initialState = {}) => {
  const [errors, setErrors] = React.useState(initialState);

  const setError = (field, message) => {
    setErrors((prev) => ({ ...prev, [field]: message }));
  };

  const clearError = (field) => {
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[field];
      return newErrors;
    });
  };

  const clearAllErrors = () => {
    setErrors({});
  };

  const hasErrors = Object.keys(errors).length > 0;

  return {
    errors,
    setError,
    clearError,
    clearAllErrors,
    hasErrors,
  };
};

// Validate entire form
export const validateForm = (formData, validationRules) => {
  const newErrors = {};

  Object.keys(validationRules).forEach((field) => {
    const rule = validationRules[field];
    const value = formData[field];

    if (typeof rule === 'function') {
      const error = rule(value);
      if (error) {
        newErrors[field] = error;
      }
    } else if (Array.isArray(rule)) {
      // Support multiple validators
      for (const validator of rule) {
        const error = validator(value);
        if (error) {
          newErrors[field] = error;
          break;
        }
      }
    }
  });

  return {
    isValid: Object.keys(newErrors).length === 0,
    errors: newErrors,
  };
};
