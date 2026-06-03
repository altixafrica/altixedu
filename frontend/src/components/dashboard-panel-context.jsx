import React, { createContext, useState, useCallback } from 'react';

export const DashboardPanelContext = createContext();

export const DashboardPanelProvider = ({ children }) => {
  const [showMessaging, setShowMessaging] = useState(false);
  const [showExport, setShowExport] = useState(false);

  const openMessaging = useCallback(() => setShowMessaging(true), []);
  const closeMessaging = useCallback(() => setShowMessaging(false), []);
  const openExport = useCallback(() => setShowExport(true), []);
  const closeExport = useCallback(() => setShowExport(false), []);

  return (
    <DashboardPanelContext.Provider
      value={{
        showMessaging,
        openMessaging,
        closeMessaging,
        showExport,
        openExport,
        closeExport,
      }}
    >
      {children}
    </DashboardPanelContext.Provider>
  );
};

export const useDashboardPanel = () => {
  const context = React.useContext(DashboardPanelContext);
  if (!context) {
    throw new Error('useDashboardPanel must be used within DashboardPanelProvider');
  }
  return context;
};
