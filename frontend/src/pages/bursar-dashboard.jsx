import React, { useEffect, useMemo, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  BarChart3,
  CreditCard,
  Download,
  Loader2,
  Receipt,
  TrendingUp,
} from 'lucide-react';

import { WorkspaceShell } from '../components/workspace-shell';
import { StatCard } from '../components/stat-card';
import { Alert, Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { getCurrentUser, getStoredSession } from '../lib/django';
import { getDashboardByRole } from '../lib/api-service';
import { formatCurrency } from '../lib/format';
import { useAuth } from '../lib/hooks';

const SectionCard = ({ title, description, children, className = '' }) => (
  <Card className={className}>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      {description ? <CardDescription>{description}</CardDescription> : null}
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);

export const BursarDashboardPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [session, setSession] = useState(() => getStoredSession());
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) return;

    const load = async () => {
      setLoading(true);
      setError('');

      try {
        const current = await getCurrentUser();
        const activeSession = current || getStoredSession();

        if (!activeSession?.role) {
          setError('Unable to determine the current user role.');
          return;
        }

        if (activeSession.role !== 'bursar') {
          navigate(`/app/${activeSession.role}`);
          return;
        }

        setSession(activeSession);
        setDashboardData(await getDashboardByRole.bursar());
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.response?.data?.detail ||
          'Unable to load the finance workspace right now.'
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isAuthenticated, navigate]);

  const school = dashboardData?.school || {};
  const financialSummary = dashboardData?.financial_summary || {};
  const feesByStatus = dashboardData?.fees_by_status || [];
  const totalStudents = dashboardData?.total_students || 0;

  const paidStatus = feesByStatus.find((entry) => entry.status === 'paid') || { count: 0, total: 0 };
  const partialStatus = feesByStatus.find((entry) => entry.status === 'partial') || { count: 0, total: 0 };
  const unpaidStatus = feesByStatus.find((entry) => entry.status === 'unpaid') || { count: 0, total: 0 };

  const statCards = useMemo(
    () => [
      {
        label: 'Total due',
        value: formatCurrency(financialSummary.total_due || 0, 'NGN'),
        detail: 'Billed student-fee obligations',
        icon: <Receipt className="h-5 w-5" />,
      },
      {
        label: 'Collected',
        value: formatCurrency(financialSummary.total_paid || 0, 'NGN'),
        detail: 'Payments already received',
        icon: <TrendingUp className="h-5 w-5" />,
        tone: 'dark',
      },
      {
        label: 'Outstanding',
        value: formatCurrency(financialSummary.balance || 0, 'NGN'),
        detail: 'Still awaiting settlement',
        icon: <AlertCircle className="h-5 w-5" />,
      },
      {
        label: 'Collection rate',
        value: `${Math.round(financialSummary.collection_rate || 0)}%`,
        detail: 'Current conversion from billed to paid',
        icon: <BarChart3 className="h-5 w-5" />,
      },
    ],
    [financialSummary]
  );

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  return (
    <WorkspaceShell
      session={session}
      role="bursar"
      currentNav="dashboard"
      eyebrow="Finance Workspace"
      title={`Collections command for ${school.name || 'your school'}`}
      description="A cleaner finance surface for fee tracking, collection health, and the actions that move payment performance."
      actions={
        <>
          <Button variant="secondary">
            <Download className="h-4 w-4" />
            Export report
          </Button>
          <Button variant="primary">
            <CreditCard className="h-4 w-4" />
            Record payment
          </Button>
        </>
      }
    >
      {loading ? (
        <div className="flex min-h-[320px] items-center justify-center">
          <div className="flex items-center gap-3 rounded-full bg-slate-950 px-5 py-3 text-white">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm font-medium">Loading finance workspace...</span>
          </div>
        </div>
      ) : error ? (
        <Alert variant="error">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5" />
            <div>
              <p className="font-medium">Finance dashboard error</p>
              <p className="mt-1 text-sm">{error}</p>
            </div>
          </div>
        </Alert>
      ) : (
        <div className="space-y-8">
          <div className="grid gap-4 xl:grid-cols-4">
            {statCards.map((card) => (
              <StatCard key={card.label} {...card} />
            ))}
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
            <div className="space-y-6">
              <SectionCard title="Collection status mix" description="How fee accounts are distributed by payment posture right now.">
                <div className="grid gap-4 md:grid-cols-3">
                  {[
                    ['Paid', paidStatus, 'success'],
                    ['Partial', partialStatus, 'warning'],
                    ['Unpaid', unpaidStatus, 'error'],
                  ].map(([label, statusItem, variant]) => (
                    <div key={label} className="rounded-[24px] border border-slate-200 bg-slate-50 px-4 py-4">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-medium text-slate-950">{label}</p>
                        <Badge variant={variant}>{statusItem.count}</Badge>
                      </div>
                      <p className="mt-4 text-2xl font-semibold text-slate-950">
                        {formatCurrency(statusItem.total || 0, 'NGN')}
                      </p>
                    </div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard title="Revenue health" description="Read the topline picture before drilling into individual records.">
                <div className="rounded-[28px] bg-slate-950 p-6 text-white">
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <p className="text-sm text-white/70">Students billed</p>
                      <p className="mt-2 text-3xl font-semibold">{totalStudents}</p>
                    </div>
                    <div>
                      <p className="text-sm text-white/70">Collected</p>
                      <p className="mt-2 text-3xl font-semibold">{formatCurrency(financialSummary.total_paid || 0, 'NGN')}</p>
                    </div>
                    <div>
                      <p className="text-sm text-white/70">Still due</p>
                      <p className="mt-2 text-3xl font-semibold">{formatCurrency(financialSummary.balance || 0, 'NGN')}</p>
                    </div>
                  </div>
                  <div className="mt-6">
                    <div className="flex items-center justify-between text-sm text-white/70">
                      <span>Collection progress</span>
                      <span>{Math.round(financialSummary.collection_rate || 0)}%</span>
                    </div>
                    <div className="mt-2 h-2 rounded-full bg-white/15">
                      <div
                        className="h-2 rounded-full bg-emerald-400"
                        style={{ width: `${Math.min(financialSummary.collection_rate || 0, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </SectionCard>
            </div>

            <div className="space-y-6">
              <SectionCard title="Action stack" description="The highest-frequency finance moves, kept close.">
                <div className="space-y-3">
                  <Button fullWidth variant="primary">
                    <CreditCard className="h-4 w-4" />
                    Record payment
                  </Button>
                  <Button fullWidth variant="secondary">Generate invoice</Button>
                  <Button fullWidth variant="secondary">Send reminders</Button>
                  <Button fullWidth variant="secondary">Export aging report</Button>
                </div>
              </SectionCard>

              <SectionCard title="Collection notes" description="A short operational summary for the school finance desk.">
                <div className="space-y-3">
                  <div className="rounded-[22px] bg-slate-50 px-4 py-4">
                    <p className="text-sm text-slate-500">Fully settled records</p>
                    <p className="mt-2 text-2xl font-semibold text-slate-950">{paidStatus.count}</p>
                  </div>
                  <div className="rounded-[22px] bg-slate-50 px-4 py-4">
                    <p className="text-sm text-slate-500">Need follow-up</p>
                    <p className="mt-2 text-2xl font-semibold text-slate-950">{partialStatus.count + unpaidStatus.count}</p>
                  </div>
                  {(financialSummary.balance || 0) > 0 ? (
                    <Alert variant="warning">
                      <div className="flex items-start gap-3">
                        <AlertCircle className="mt-0.5 h-5 w-5" />
                        <div>
                          <p className="font-medium">Outstanding receivables remain</p>
                          <p className="mt-1 text-sm">
                            There is still an open balance across fee accounts. Reminder and outreach flows should remain active.
                          </p>
                        </div>
                      </div>
                    </Alert>
                  ) : null}
                </div>
              </SectionCard>
            </div>
          </div>
        </div>
      )}
    </WorkspaceShell>
  );
};
