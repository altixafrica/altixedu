import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export const SiteHeader = () => {
  const isAuthenticated =
    typeof window !== 'undefined' && Boolean(localStorage.getItem('auth_token'));

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/70 bg-white/88 backdrop-blur-xl">
      <div className="container mx-auto flex h-18 items-center justify-between px-4 py-4 md:px-6">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-950 text-sm font-semibold text-white shadow-lg shadow-slate-950/10">
            AE
          </div>
          <div>
            <span className="block text-lg font-semibold text-slate-950">AltixEdu</span>
            <span className="block text-[11px] uppercase tracking-[0.18em] text-slate-500">
              Education Operations
            </span>
          </div>
        </Link>
        <nav className="hidden items-center gap-8 md:flex">
          <Link to="/school-admins" className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-950">
            Administrators
          </Link>
          <Link to="/teachers" className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-950">
            Teachers
          </Link>
          <Link to="/parents" className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-950">
            Families
          </Link>
          <Link to="/pricing" className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-950">
            Pricing
          </Link>
          <Link
            to={isAuthenticated ? '/dashboard' : '/login'}
            className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-4 py-2 text-sm font-medium text-white transition-transform hover:-translate-y-0.5"
          >
            {isAuthenticated ? 'Open workspace' : 'Sign in'}
            <ArrowRight className="h-4 w-4" />
          </Link>
        </nav>
      </div>
    </header>
  );
};
