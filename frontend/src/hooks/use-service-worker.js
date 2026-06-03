import { useEffect } from 'react';

export const useServiceWorker = () => {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      // Register service worker
      navigator.serviceWorker.register('/sw.js')
        .then((registration) => {
          console.log('Service Worker registered:', registration);

          // Check for updates periodically
          setInterval(() => {
            registration.update();
          }, 60000); // Check every minute

          // Listen for new service worker
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'activated') {
                console.log('New Service Worker activated');
                // Optionally notify user of update
              }
            });
          });
        })
        .catch((error) => {
          console.log('Service Worker registration failed:', error);
        });
    }
  }, []);
};
