import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

export const usePageTransition = () => {
  const [isTransitioning, setIsTransitioning] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setIsTransitioning(true);
    const timer = setTimeout(() => setIsTransitioning(false), 50);
    return () => clearTimeout(timer);
  }, [location.pathname]);

  return { isTransitioning };
};

export const PageTransition = ({ children }) => {
  const { isTransitioning } = usePageTransition();

  return (
    <div
      className={`transition-all duration-300 ease-out ${
        isTransitioning ? 'opacity-50' : 'opacity-100'
      }`}
    >
      {children}
    </div>
  );
};
