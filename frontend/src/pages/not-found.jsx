import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';

export const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-brand-600 mb-4">404</h1>
        <p className="text-2xl font-semibold text-slate-900 mb-2">Page not found</p>
        <p className="text-slate-600 mb-8">The page you are looking for does not exist.</p>
        <Link to="/">
          <Button>Go home</Button>
        </Link>
      </div>
    </div>
  );
};
