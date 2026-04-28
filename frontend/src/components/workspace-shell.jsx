import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  BadgeDollarSign,
  BookOpen,
  Building2,
  GraduationCap,
  Home,
  LogOut,
  Settings,
  Shield,
  Users,
} from 'lucide-react';

import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { logoutUser } from '../lib/django';

const NAV_ITEMS = {
  admin: [
    { key: 'dashboard', label: 'Overview', href: '/dashboard', icon: Home },
    { key: 'users', label: 'User Management', href: '/app/admin/users', icon: Users },
    { key: 'settings', label: 'Settings', href: '/app/admin/settings', icon: Settings },
  ],
  teacher: [
    { key: 'dashboard', label: 'Workspace', href: '/app/teacher', icon: GraduationCap },
  ],
  student: [
    { key: 'dashboard', label: 'Workspace', href: '/app/student', icon: BookOpen },
  ],
  parent: [
    { key: 'dashboard', label: 'Family Portal', href: '/app/parent', icon: Users },
  ],
  bursar: [
    { key: 'dashboard', label: 'Finance', href: '/app/bursar', icon: BadgeDollarSign },
  ],
  superadmin: [
    { key: 'dashboard', label: 'Portfolio', href: '/dashboard', icon: Shield },
  ],
  ministry_admin: [
    { key: 'dashboard', label: 'Ministry View', href: '/dashboard', icon: Building2 },
  ],
};

export const WorkspaceShell = ({
  session,
  role,
  currentNav = 'dashboard',
  eyebrow,
  title,
  description,
  actions,
  children,
}) => {
  const navigate = useNavigate();
  const items = NAV_ITEMS[role] || NAV_ITEMS.admin;
  const workspaceName = session?.school?.name || session?.ministry?.name || 'AltixEdu';
  const userName =
    session?.user?.full_name ||
    session?.user?.first_name ||
    session?.user?.username ||
    'Workspace user';

  const handleLogout = async () => {
    await logoutUser();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="mx-auto grid min-h-screen max-w-[1600px] lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="hidden border-r border-white/10 bg-slate-950 px-6 py-8 text-white lg:block">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white text-sm font-semibold text-slate-950">
              AE
            </div>
            <div>
              <p className="text-lg font-semibold">AltixEdu</p>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Workspace</p>
            </div>
          </Link>

          <div className="mt-10 rounded-[28px] border border-white/8 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Organization</p>
            <p className="mt-2 text-base font-medium text-white">{workspaceName}</p>
            <p className="mt-1 text-sm text-slate-400">{userName}</p>
          </div>

          <nav className="mt-8 space-y-2">
            {items.map((item) => {
              const Icon = item.icon;
              const active = item.key === currentNav;
              return (
                <Link
                  key={item.key}
                  to={item.href}
                  className={`flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                    active
                      ? 'bg-white text-slate-950'
                      : 'text-slate-300 hover:bg-white/[0.05] hover:text-white'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="mt-auto pt-8">
            <Button variant="secondary" fullWidth onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
              Sign out
            </Button>
          </div>
        </aside>

        <main className="min-w-0 px-4 py-4 md:px-6 md:py-6 lg:px-8 lg:py-8">
          <div className="rounded-[30px] border border-slate-200 bg-white shadow-sm shadow-slate-950/[0.03]">
            <header className="border-b border-slate-200 px-5 py-5 md:px-8 md:py-7">
              <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
                <div className="max-w-3xl">
                  {eyebrow ? (
                    <Badge className="bg-slate-950 text-white">{eyebrow}</Badge>
                  ) : null}
                  <h1 className="mt-4 text-balance text-3xl font-semibold tracking-tight text-slate-950 md:text-4xl">
                    {title}
                  </h1>
                  {description ? (
                    <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 md:text-base">
                      {description}
                    </p>
                  ) : null}
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  {actions}
                  <div className="lg:hidden">
                    <Button variant="outline" onClick={handleLogout}>
                      <LogOut className="h-4 w-4" />
                      Sign out
                    </Button>
                  </div>
                </div>
              </div>

              <div className="mt-5 flex gap-2 overflow-x-auto pb-1 lg:hidden">
                {items.map((item) => {
                  const Icon = item.icon;
                  const active = item.key === currentNav;
                  return (
                    <Link
                      key={item.key}
                      to={item.href}
                      className={`inline-flex min-w-fit items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                        active
                          ? 'bg-slate-950 text-white'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </header>

            <div className="px-5 py-6 md:px-8 md:py-8">{children}</div>
          </div>
        </main>
      </div>
    </div>
  );
};
