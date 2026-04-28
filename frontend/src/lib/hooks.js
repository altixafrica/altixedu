import React from 'react';

export const useAuth = () => {
  const token = localStorage.getItem('auth_token');

  let user = null;
  let session = null;

  try {
    const rawUser = localStorage.getItem('user');
    user = rawUser ? JSON.parse(rawUser) : null;
  } catch (error) {
    console.error('Failed to parse stored user:', error);
  }

  try {
    const rawSession = localStorage.getItem('auth_session');
    session = rawSession ? JSON.parse(rawSession) : null;
  } catch (error) {
    console.error('Failed to parse stored session:', error);
  }

  return {
    user,
    session,
    token,
    isAuthenticated: !!token,
  };
};

export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = React.useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
};
