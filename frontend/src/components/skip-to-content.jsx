import React from 'react';
import { Button } from './ui/button';

/**
 * Skip to Main Content Link
 * WCAG 2.1 A11y best practice - allows keyboard users to skip navigation
 * Should be first visible element when tabbed into page
 */
export const SkipToContentLink = ({ mainContentId = 'main-content' }) => {
  return (
    <a
      href={`#${mainContentId}`}
      className="absolute -top-full left-0 z-50 bg-brand-600 text-white px-4 py-2 text-sm font-medium focus:top-0"
      onClick={(e) => {
        e.preventDefault();
        document.getElementById(mainContentId)?.focus();
      }}
    >
      Skip to main content
    </a>
  );
};
