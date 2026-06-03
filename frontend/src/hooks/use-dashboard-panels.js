import { useState, useCallback } from 'react';

/**
 * Hook to manage messaging and export panel states in dashboard
 */
export const useDashboardPanels = () => {
  const [showMessaging, setShowMessaging] = useState(false);
  const [showExport, setShowExport] = useState(false);

  const openMessaging = useCallback(() => setShowMessaging(true), []);
  const closeMessaging = useCallback(() => setShowMessaging(false), []);
  const openExport = useCallback(() => setShowExport(true), []);
  const closeExport = useCallback(() => setShowExport(false), []);

  return {
    showMessaging,
    openMessaging,
    closeMessaging,
    showExport,
    openExport,
    closeExport,
  };
};
