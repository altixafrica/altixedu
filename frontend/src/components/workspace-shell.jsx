import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  BadgeDollarSign,
  BookOpen,
  Building2,
  Download,
  GraduationCap,
  Home,
  LogOut,
  MessageSquare,
  Settings,
  Shield,
  Users,
  Bell,
} from 'lucide-react';

import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { logoutUser } from '../lib/django';
import { useDashboardPanel } from './dashboard-panel-context';
import { EnhancedMessagingPanel } from './enhanced-messaging-panel';
import { ExportPanel } from './export-handler';
import { AdminAnnouncementManager } from './admin-announcement-manager';

const NAV_ITEMS = {
  admin: [
    { key: 'dashboard', label: 'Overview', href: '/dashboard', icon: Home },
    { key: 'announcements', label: 'Announcements', href: '#announcements', icon: Bell },
    { key: 'messaging', label: 'Messages', href: '#messaging', icon: MessageSquare },
    { key: 'export', label: 'Export Data', href: '#export', icon: Download },
    { key: 'users', label: 'User Management', href: '/app/admin/users', icon: Users },
    { key: 'settings', label: 'Settings', href: '/app/admin/settings', icon: Settings },
  ],
  teacher: [
    { key: 'dashboard', label: 'Workspace', href: '/app/teacher', icon: GraduationCap },
    { key: 'messaging', label: 'Messages', href: '#messaging', icon: MessageSquare },
    { key: 'export', label: 'Export', href: '#export', icon: Download },
  ],
  student: [
    { key: 'dashboard', label: 'Workspace', href: '/app/student', icon: BookOpen },
    { key: 'messaging', label: 'Messages', href: '#messaging', icon: MessageSquare },
  ],
  parent: [
    { key: 'dashboard', label: 'Family Portal', href: '/app/parent', icon: Users },
    { key: 'messaging', label: 'Messages', href: '#messaging', icon: MessageSquare },
  ],
  bursar: [
    { key: 'dashboard', label: 'Finance', href: '/app/bursar', icon: BadgeDollarSign },
    { key: 'messaging', label: 'Messages', href: '#messaging', icon: MessageSquare },
    { key: 'export', label: 'Export', href: '#export', icon: Download },
  ],
  superadmin: [
    { key: 'dashboard', label: 'Portfolio', href: '/dashboard', icon: Shield },
    { key: 'messaging', label: 'Messages', href: '#messaging', icon: MessageSquare },
  ],
  ministry_admin: [
    { key: 'dashboard', label: 'Ministry View', href: '/dashboard', icon: Building2 },
    { key: 'messaging', label: 'Messages', href: '#messaging', icon: MessageSquare },
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
  const [showAnnouncements, setShowAnnouncements] = useState(false);
  const { openMessaging, openExport, showMessaging, closeMessaging, showExport, closeExport } = useDashboardPanel();
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
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <div className="mx-auto grid min-h-screen max-w-[1680px] lg:grid-cols-[248px_minmax(0,1fr)]">
        <aside className="hidden border-r border-slate-200 bg-white px-5 py-6 text-slate-950 dark:border-slate-800 dark:bg-slate-950 dark:text-white lg:block">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-950 text-sm font-semibold text-white dark:bg-white dark:text-slate-950">
              AE
            </div>
            <div>
              <p className="text-base font-semibold">AltixEdu</p>
              <p className="text-[11px] uppercase tracking-[0.14em] text-slate-500">Workspace</p>
            </div>
          </Link>

          <div className="mt-8 border-y border-slate-200 py-4 dark:border-slate-800">
            <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Organization</p>
            <p className="mt-2 truncate text-sm font-medium text-slate-950 dark:text-white">{workspaceName}</p>
            <p className="mt-1 truncate text-sm text-slate-500 dark:text-slate-400">{userName}</p>
          </div>

          <nav className="mt-6 space-y-1">
            {items.map((item) => {
              const Icon = item.icon;
              const active = item.key === currentNav;
              const isHash = item.href.startsWith('#');
              
              const handleClick = (e) => {
                if (isHash) {
                  e.preventDefault();
                  if (item.key === 'messaging') {
                    openMessaging();
                  } else if (item.key === 'export') {
                    openExport();
                  } else if (item.key === 'announcements') {
                    setShowAnnouncements(true);
                  }
                }
              };
              
              return (
                <Link
                  key={item.key}
                  to={item.href}
                  onClick={handleClick}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                    active
                      ? 'bg-slate-950 text-white dark:bg-white dark:text-slate-950'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white'
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

        <main className="min-w-0 px-4 py-4 md:px-6 md:py-6 lg:px-8">
          <div className="bg-white dark:bg-slate-900">
            <header className="border-b border-slate-200 py-5 dark:border-slate-800 md:py-6">
              <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
                <div className="max-w-3xl">
                  {eyebrow ? (
                    <Badge className="bg-slate-950 text-white dark:bg-white dark:text-slate-950">{eyebrow}</Badge>
                  ) : null}
                  <h1 className="mt-3 text-balance text-2xl font-semibold tracking-tight text-slate-950 dark:text-white md:text-3xl">
                    {title}
                  </h1>
                  {description ? (
                    <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600 dark:text-slate-400">
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
                      onClick={(event) => {
                        if (item.href.startsWith('#')) {
                          event.preventDefault();
                          if (item.key === 'messaging') openMessaging();
                          if (item.key === 'export') openExport();
                          if (item.key === 'announcements') setShowAnnouncements(true);
                        }
                      }}
                      className={`inline-flex min-w-fit items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition ${
                        active
                          ? 'bg-slate-950 text-white dark:bg-slate-700'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </header>

            <div className="py-6 md:py-8">{children}</div>
          </div>
        </main>
      </div>

      {/* Messaging, Announcements, and Export Panels */}
      <EnhancedMessagingPanel isOpen={showMessaging} onClose={closeMessaging} currentUser={session?.user} />
      <ExportPanel isOpen={showExport} onClose={closeExport} />
      {showAnnouncements && (
        <AdminAnnouncementManager
          schoolId={session?.school?.id}
          userRole={role}
          onClose={() => setShowAnnouncements(false)}
        />
      )}
    </div>
  );
};
