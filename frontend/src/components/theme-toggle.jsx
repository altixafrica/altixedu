import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../lib/theme-context';
import { Button } from './ui/button';

/**
 * Theme Toggle Component
 * Allows users to switch between light and dark modes
 */
export const ThemeToggle = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <Button
      onClick={toggleTheme}
      variant="ghost"
      size="sm"
      ariaLabel={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      className="rounded-full"
    >
      {isDark ? (
        <Sun size={18} className="text-yellow-400" />
      ) : (
        <Moon size={18} className="text-slate-600" />
      )}
    </Button>
  );
};
