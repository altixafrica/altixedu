import React, { useEffect, useMemo, useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  ArrowRight,
  Building2,
  GraduationCap,
  Landmark,
  Loader2,
  Receipt,
  Shield,
  Users,
} from 'lucide-react';

import { WorkspaceShell } from '../components/workspace-shell';
import { StatCard } from '../components/stat-card';
import { Alert, Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { SkeletonGrid, SkeletonChart } from '../components/skeleton-loader';
import { SmartInsight, generateInsights } from '../components/smart-insights';
import { FeeCollectionChart, StudentPerformanceChart, AttendanceChart, PaymentStatusChart, SubscriptionHealthChart, MinistryPerformanceChart } from '../components/dashboard-charts';
import { getDashboardData, getCurrentUser, getStoredSession, logoutUser } from '../lib/django';
import { formatCurrency, formatDate, titleize } from '../lib/format';
import { useAuth } from '../lib/hooks';

const ROLE_META = {
  admin: {
    eyebrow: 'School Command',
    title: 'Today at a glance',
    description: 'Enrollment, fee movement, staff coverage, and learner risk in one calm operating view.',
  },
  superadmin: {
    eyebrow: 'Platform Portfolio',
    title: 'Portfolio health',
    description: 'Subscription health, revenue signals, watchlist accounts, and network momentum.',
  },
  ministry_admin: {
    eyebrow: 'Ministry View',
    title: 'State education oversight',
    description: 'Coverage, attendance, finance movement, and urgent operating signals across schools.',
  },
};

const toArray = (value) => (Array.isArray(value) ? value : []);

const Panel = ({ title, description, children, className = '' }) => (
  <Card className={className}>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      {description ? <CardDescription>{description}</CardDescription> : null}
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);

const EmptyState = ({ children }) => (
  <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-500">
    {children}
  </div>
);

export const DashboardPage = () => {
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
          setError('We could not determine the current user role.');
          return;
        }

        if (!['admin', 'superadmin', 'ministry_admin'].includes(activeSession.role)) {
          navigate(`/app/${activeSession.role}`);
          return;
        }

        setSession(activeSession);
        setDashboardData(await getDashboardData(activeSession));
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.response?.data?.detail ||
          'Unable to load dashboard data right now.'
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isAuthenticated, navigate]);

  const handleLogout = async () => {
    await logoutUser();
    navigate('/login');
  };

  const role = session?.role || 'admin';
  const roleMeta = ROLE_META[role] || ROLE_META.admin;
  const currencyCode = session?.ministry?.currency_code || dashboardData?.currency || 'NGN';

  const summaryCards = useMemo(() => {
    if (!dashboardData) return [];

    if (role === 'admin') {
      const stats = dashboardData.statistics || {};
      const finance = dashboardData.finance || {};
      return [
        { label: 'Students', value: stats.total_students || 0, icon: <Users className="h-5 w-5" />, detail: 'Active learner records' },
        { label: 'Teachers', value: stats.total_teachers || 0, icon: <GraduationCap className="h-5 w-5" />, detail: 'Teaching staff accounts' },
        { label: 'Collections', value: `${Math.round(finance.collection_percentage || 0)}%`, icon: <Receipt className="h-5 w-5" />, detail: 'Fee collection efficiency', tone: 'dark' },
        { label: 'At-risk students', value: stats.at_risk_students || 0, icon: <AlertCircle className="h-5 w-5" />, detail: 'Require follow-up this week' },
      ];
    }

    if (role === 'superadmin') {
      const summary = dashboardData.summary || {};
      return [
        { label: 'Schools', value: summary.schools_with_subscriptions || 0, icon: <Building2 className="h-5 w-5" />, detail: 'Provisioned workspaces' },
        { label: 'Active subscriptions', value: summary.active_subscriptions || 0, icon: <Shield className="h-5 w-5" />, detail: 'Revenue-producing accounts' },
        { label: 'MRR', value: formatCurrency(summary.estimated_monthly_run_rate || 0, currencyCode), icon: <Receipt className="h-5 w-5" />, detail: 'Estimated monthly run rate', tone: 'dark' },
        { label: 'Renewals due', value: summary.renewals_next_30_days || 0, icon: <AlertCircle className="h-5 w-5" />, detail: 'In the next 30 days' },
      ];
    }

    const ministry = dashboardData || {};
    return [
      { label: 'Schools', value: ministry.total_schools || 0, icon: <Building2 className="h-5 w-5" />, detail: 'Connected school network' },
      { label: 'Students', value: ministry.total_students || 0, icon: <Users className="h-5 w-5" />, detail: 'Learners under oversight' },
      { label: 'Collection rate', value: `${Math.round(ministry.collection_rate_percentage || 0)}%`, icon: <Receipt className="h-5 w-5" />, detail: 'Statewide fee performance', tone: 'dark' },
      { label: 'Students at risk', value: ministry.students_at_risk_count || 0, icon: <AlertCircle className="h-5 w-5" />, detail: 'Flagged for intervention' },
    ];
  }, [dashboardData, role, currencyCode]);

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  return (
    <WorkspaceShell
      session={session}
      role={role}
      currentNav="dashboard"
      eyebrow={roleMeta.eyebrow}
      title={roleMeta.title}
      description={roleMeta.description}
      actions={
        <>
          <Link to="/">
            <Button variant="secondary">Public site</Button>
          </Link>
          <Button variant="outline" onClick={handleLogout}>Sign out</Button>
        </>
      }
    >
      {loading ? (
        <div className="space-y-6">
          <SkeletonGrid columns={4} />
          <SkeletonChart />
        </div>
      ) : error ? (
        <Alert variant="error">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5" />
            <div>
              <p className="font-medium">Dashboard error</p>
              <p className="mt-1 text-sm">{error}</p>
            </div>
          </div>
        </Alert>
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 xl:grid-cols-4">
            {summaryCards.map((card) => <StatCard key={card.label} {...card} />)}
          </div>

          {/* Smart Insights Section */}
          {role === 'admin' && (
            <div>
              <div className="mb-4">
                <h2 className="text-lg font-semibold text-slate-950">Key Insights</h2>
                <p className="text-sm text-slate-500">Data-driven alerts and recommendations</p>
              </div>
              <div className="grid gap-3">
                {generateInsights(dashboardData, role).slice(0, 3).map((insight, idx) => (
                  <SmartInsight
                    key={idx}
                    type={insight.type}
                    title={insight.title}
                    message={insight.message}
                    action={insight.action}
                    confidence={insight.confidence}
                  />
                ))}
              </div>
            </div>
          )}

          {role === 'admin' ? (
            <>
              {/* Charts Section */}
              <div className="grid gap-6 xl:grid-cols-2">
                <FeeCollectionChart />
                <StudentPerformanceChart />
              </div>
              <div className="grid gap-6 xl:grid-cols-2">
                <AttendanceChart />
                <PaymentStatusChart />
              </div>
            </>
          ) : role === 'superadmin' ? (
            <div className="grid gap-6 xl:grid-cols-1">
              <SubscriptionHealthChart />
            </div>
          ) : role === 'ministry_admin' ? (
            <div className="grid gap-6 xl:grid-cols-1">
              <MinistryPerformanceChart />
            </div>
          ) : null}

          {role === 'admin' ? (
            <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
              <div className="space-y-6">
                <Panel title="Learner follow-up" description="Students who need action before the week slips away.">
                  <div className="space-y-3">
                    {toArray(dashboardData.at_risk_alerts).slice(0, 6).map((student) => (
                      <div key={student.student_id} className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 md:flex-row md:items-center md:justify-between">
                        <div>
                          <p className="font-medium text-slate-950">{student.student_name}</p>
                          <p className="mt-1 text-sm text-slate-500">{student.classroom || 'No classroom assigned'}</p>
                        </div>
                        <div className="text-sm text-slate-600 md:text-right">
                          <p>{Math.round((student.performance_risk || 0) * 100)}% performance risk</p>
                          <p>{Math.round((student.attendance_risk || 0) * 100)}% attendance risk</p>
                        </div>
                      </div>
                    ))}
                    {!toArray(dashboardData.at_risk_alerts).length ? (
                      <EmptyState>No learner is currently flagged for immediate follow-up.</EmptyState>
                    ) : null}
                  </div>
                </Panel>

                <Panel title="Recent students" description="Latest records to inspect or complete.">
                  <div className="grid gap-3 md:grid-cols-2">
                    {toArray(dashboardData.students).slice(0, 6).map((student) => (
                      <div key={student.id} className="rounded-lg border border-slate-200 px-4 py-3">
                        <p className="font-medium text-slate-950">{student.first_name} {student.last_name}</p>
                        <p className="mt-1 text-sm text-slate-500">{student.classroom || 'No classroom'} / {titleize(student.status || 'active')}</p>
                      </div>
                    ))}
                    {!toArray(dashboardData.students).length ? <EmptyState>No recent student records yet.</EmptyState> : null}
                  </div>
                </Panel>
              </div>

              <div className="space-y-6">
                <Panel title="School structure" description="Core operating volume.">
                  <div className="grid gap-3">
                    {[
                      ['Classrooms', dashboardData.statistics?.total_classrooms || 0],
                      ['Subjects', dashboardData.statistics?.total_subjects || 0],
                      ['Students', dashboardData.statistics?.total_students || 0],
                      ['Teachers', dashboardData.statistics?.total_teachers || 0],
                    ].map(([label, value]) => (
                      <div key={label} className="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3">
                        <span className="text-sm text-slate-600">{label}</span>
                        <span className="text-base font-semibold text-slate-950">{value}</span>
                      </div>
                    ))}
                  </div>
                </Panel>

                <Panel title="Financial pulse" description="Collection posture for the current cycle.">
                  <div className="space-y-3">
                    <div className="rounded-lg bg-slate-950 p-5 text-white">
                      <p className="text-sm text-white/70">Outstanding balance</p>
                      <p className="mt-2 text-2xl font-semibold">
                        {formatCurrency(dashboardData.finance?.total_outstanding || 0, currencyCode)}
                      </p>
                    </div>
                    <div className="rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-600">
                      Fees collected: {formatCurrency(dashboardData.finance?.total_paid || 0, currencyCode)}
                    </div>
                  </div>
                </Panel>

                <Panel title="Teaching staff" description="Current teacher accounts.">
                  <div className="space-y-3">
                    {toArray(dashboardData.teachers).slice(0, 5).map((teacher) => (
                      <div key={teacher.id} className="rounded-lg border border-slate-200 px-4 py-3">
                        <p className="font-medium text-slate-950">{teacher.first_name} {teacher.last_name}</p>
                        <p className="mt-1 text-sm text-slate-500">{teacher.email}</p>
                      </div>
                    ))}
                    {!toArray(dashboardData.teachers).length ? <EmptyState>No teacher records yet.</EmptyState> : null}
                  </div>
                </Panel>
              </div>
            </div>
          ) : role === 'superadmin' ? (
            <div className="grid gap-6 xl:grid-cols-3">
              <Panel title="Tier mix" description="Subscription concentration across plans.">
                <div className="space-y-3">
                  {toArray(dashboardData.tier_mix).map((tier) => (
                    <div key={tier.tier_name} className="rounded-lg border border-slate-200 px-4 py-3">
                      <p className="font-medium text-slate-950">{tier.tier_name}</p>
                      <p className="mt-1 text-sm text-slate-500">{tier.schools} schools</p>
                    </div>
                  ))}
                  {!toArray(dashboardData.tier_mix).length ? <EmptyState>No tier data available yet.</EmptyState> : null}
                </div>
              </Panel>

              <Panel title="Watchlist" description="Accounts needing attention soonest.">
                <div className="space-y-3">
                  {toArray(dashboardData.watchlist).slice(0, 6).map((item) => (
                    <div key={item.subscription_id} className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                      <p className="font-medium text-slate-950">{item.school_name}</p>
                      <p className="mt-1 text-sm text-slate-500">{titleize(item.status)} / {item.days_until_renewal} days</p>
                    </div>
                  ))}
                  {!toArray(dashboardData.watchlist).length ? <EmptyState>No renewal or billing watchlist items.</EmptyState> : null}
                </div>
              </Panel>

              <Panel title="Recent transactions" description="Latest billing movement.">
                <div className="space-y-3">
                  {toArray(dashboardData.recent_transactions).slice(0, 6).map((transaction) => (
                    <div key={transaction.id} className="rounded-lg border border-slate-200 px-4 py-3">
                      <p className="font-medium text-slate-950">{transaction.school_name}</p>
                      <p className="mt-1 text-sm text-slate-500">{titleize(transaction.status)} / {formatDate(transaction.created_at)}</p>
                    </div>
                  ))}
                  {!toArray(dashboardData.recent_transactions).length ? <EmptyState>No recent transactions.</EmptyState> : null}
                </div>
              </Panel>
            </div>
          ) : (
            <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
              <Panel title="State performance" description="Coverage and finance movement across the ministry network.">
                <div className="grid gap-4 md:grid-cols-2">
                  {[
                    ['Fees collected', formatCurrency(dashboardData.total_fees_collected || 0, currencyCode)],
                    ['Outstanding fees', formatCurrency(dashboardData.total_fees_outstanding || 0, currencyCode)],
                    ['Average attendance', `${Math.round(dashboardData.avg_attendance_rate || 0)}%`],
                    ['Pass rate', `${Math.round(dashboardData.overall_pass_rate || 0)}%`],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-lg border border-slate-200 bg-slate-50 p-5">
                      <p className="text-sm text-slate-500">{label}</p>
                      <p className="mt-3 text-2xl font-semibold text-slate-950">{value}</p>
                    </div>
                  ))}
                </div>
              </Panel>

              <Panel title="Alerts" description="Recent ministry-level attention signals.">
                <div className="space-y-3">
                  {toArray(dashboardData.alerts).slice(0, 6).map((alert) => (
                    <div key={alert.id} className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                      <p className="font-medium text-slate-950">{alert.title || 'State alert'}</p>
                      <p className="mt-2 text-sm leading-6 text-slate-600">{alert.message}</p>
                    </div>
                  ))}
                  {!toArray(dashboardData.alerts).length ? <EmptyState>No ministry alerts right now.</EmptyState> : null}
                </div>
              </Panel>
            </div>
          )}

          <div className="rounded-lg border border-slate-200 bg-slate-50 px-5 py-5">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm font-medium text-slate-950">Secondary tools live in the sidebar.</p>
                <p className="mt-1 text-sm text-slate-600">Messages, announcements, exports, and settings stay available without crowding the main dashboard.</p>
              </div>
              <Link to="/">
                <Button variant="secondary">
                  Public site
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}
    </WorkspaceShell>
  );
};
