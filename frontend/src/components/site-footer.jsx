import React from 'react';
import { Link } from 'react-router-dom';

export const SiteFooter = () => {
  return (
    <footer className="border-t border-slate-200 bg-slate-950 py-16 text-slate-300">
      <div className="container mx-auto px-4 md:px-6">
        <div className="grid gap-10 md:grid-cols-[1.5fr_1fr_1fr_1fr]">
          <div>
            <h3 className="mb-4 text-lg font-semibold text-white">AltixEdu</h3>
            <p className="max-w-sm text-sm leading-6 text-slate-400">
              AltixEdu helps schools, educators, and families operate with more clarity across academics, attendance, billing, and communication.
            </p>
          </div>
          <div>
            <h4 className="mb-4 text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">Product</h4>
            <ul className="space-y-3 text-sm text-slate-400">
              <li><Link to="/school-admins" className="hover:text-white">Administrators</Link></li>
              <li><Link to="/teachers" className="hover:text-white">Teachers</Link></li>
              <li><Link to="/parents" className="hover:text-white">Families</Link></li>
              <li><Link to="/pricing" className="hover:text-white">Pricing</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="mb-4 text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">Platform</h4>
            <ul className="space-y-3 text-sm text-slate-400">
              <li><span>Attendance and analytics</span></li>
              <li><span>Billing and collections</span></li>
              <li><span>Role-based workspaces</span></li>
            </ul>
          </div>
          <div>
            <h4 className="mb-4 text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">Access</h4>
            <ul className="space-y-3 text-sm text-slate-400">
              <li><Link to="/login" className="hover:text-white">Sign in</Link></li>
              <li><Link to="/get-started" className="hover:text-white">Create workspace</Link></li>
              <li><Link to="/pricing" className="hover:text-white">Compare plans</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-12 border-t border-slate-800 pt-8 text-sm text-slate-500">
          <p> 2026 AltixEdu. Built for modern education teams.</p>
        </div>
      </div>
    </footer>
  );
};
