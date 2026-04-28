import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

const RouterContext = createContext({
  location: '/',
  navigate: () => {},
});

const normalizePath = (value) => {
  if (!value) return '/';
  const trimmed = value.replace(/\/+$/, '');
  return trimmed || '/';
};

const getCurrentPath = () => normalizePath(window.location.pathname || '/');

const matchPath = (routePath, currentPath) => {
  if (routePath === '*') return true;
  return normalizePath(routePath) === normalizePath(currentPath);
};

export const BrowserRouter = ({ children }) => {
  const [location, setLocation] = useState(getCurrentPath);

  useEffect(() => {
    const handleLocationChange = () => setLocation(getCurrentPath());
    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  const navigate = (to, options = {}) => {
    const nextPath = normalizePath(to);
    const method = options.replace ? 'replaceState' : 'pushState';
    window.history[method]({}, '', nextPath);
    setLocation(nextPath);
  };

  const value = useMemo(() => ({ location, navigate }), [location]);

  return <RouterContext.Provider value={value}>{children}</RouterContext.Provider>;
};

export const Routes = ({ children }) => {
  const { location } = useContext(RouterContext);
  const routeList = React.Children.toArray(children).filter(Boolean);

  for (const child of routeList) {
    if (!React.isValidElement(child)) continue;
    if (matchPath(child.props.path, location)) {
      return child.props.element ?? null;
    }
  }

  return null;
};

export const Route = () => null;

export const Navigate = ({ to, replace = false }) => {
  const { navigate } = useContext(RouterContext);

  useEffect(() => {
    navigate(to, { replace });
  }, [navigate, replace, to]);

  return null;
};

export const Link = ({ to, onClick, children, ...props }) => {
  const { navigate } = useContext(RouterContext);

  return (
    <a
      href={to}
      onClick={(event) => {
        onClick?.(event);
        if (
          event.defaultPrevented ||
          event.metaKey ||
          event.ctrlKey ||
          event.shiftKey ||
          event.altKey
        ) {
          return;
        }

        event.preventDefault();
        navigate(to);
      }}
      {...props}
    >
      {children}
    </a>
  );
};

export const useNavigate = () => {
  const { navigate } = useContext(RouterContext);
  return navigate;
};
