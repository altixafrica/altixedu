import React, { useEffect, useMemo, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  CalendarDays,
  CreditCard,
  Loader2,
  MessageSquare,
  ShieldCheck,
  Sparkles,
  Users,
} from 'lucide-react';

import { WorkspaceShell } from '../components/workspace-shell';
import { StatCard } from '../components/stat-card';
import { Alert, Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { getCurrentUser, getStoredSession } from '../lib/django';
import { getDashboardByRole } from '../lib/api-service';
import { formatCurrency, titleize } from '../lib/format';
import { useAuth } from '../lib/hooks';

const RiskBadge = ({ level }) => {
  const variants = {
    LOW: 'success',
    MEDIUM: 'warning',
    HIGH: 'error',
  };

  return <Badge variant={variants[level] || 'default'}>{level}</Badge>;
};

const FeeStatus = ({ fee }) => {
  if (fee.paid) {
    return <Badge variant="success">Paid</Badge>;
  }
  if ((fee.balance || 0) > 0) {
    return <Badge variant="warning">{formatCurrency(fee.balance || 0, 'NGN')} due</Badge>;
  }
  return <Badge>Pending</Badge>;
};

const SectionCard = ({ title, description, children, className = '' }) => (
  <Card className={className}>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      {description ? <CardDescription>{description}</CardDescription> : null}
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);

export const ParentDashboardPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [session, setSession] = useState(() => getStoredSession());
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedChildId, setSelectedChildId] = useState(null);

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

        if (activeSession.role !== 'parent') {
          navigate(`/app/${activeSession.role}`);
          return;
        }

        setSession(activeSession);
        const payload = await getDashboardByRole.parent();
        setDashboardData(payload);

        if (payload?.children?.length) {
          setSelectedChildId(payload.children[0].id);
        }
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.response?.data?.detail ||
          'Unable to load the family portal right now.'
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isAuthenticated, navigate]);

  const children = dashboardData?.children || [];
  const fees = dashboardData?.fees || [];
  const attendance = dashboardData?.attendance || [];
  const aiInsights = dashboardData?.ai_insights || [];
  const messages = dashboardData?.messages || {};

  const selectedChild = children.find((child) => child.id === selectedChildId) || children[0];
  const selectedFee = fees.find((fee) => fee.student_id === selectedChild?.id);
  const selectedAttendance = attendance.find((entry) => entry.student_id === selectedChild?.id);
  const selectedInsight = aiInsights.find((entry) => entry.student_id === selectedChild?.id);

  const totalOutstandingFees = fees.reduce((sum, fee) => sum + (fee.balance || 0), 0);
  const childrenAtRisk = aiInsights.filter((entry) => (entry.attendance_risk || 0) > 0.45 || (entry.performance_risk || 0) > 0.45).length;

  const statCards = useMemo(
    () => [
      {
        label: 'Children',
        value: children.length,
        detail: 'Learners linked to this guardian account',
        icon: <Users className="h-5 w-5" />,
      },
      {
        label: 'Outstanding balance',
        value: formatCurrency(totalOutstandingFees, 'NGN'),
        detail: 'Across all linked children',
        icon: <CreditCard className="h-5 w-5" />,
        tone: 'dark',
      },
      {
        label: 'At-risk alerts',
        value: childrenAtRisk,
        detail: 'Children needing closer attention',
        icon: <Sparkles className="h-5 w-5" />,
      },
      {
        label: 'Unread messages',
        value: messages.unread_count || 0,
        detail: 'School communication waiting',
        icon: <MessageSquare className="h-5 w-5" />,
      },
    ],
    [children.length, childrenAtRisk, messages.unread_count, totalOutstandingFees]
  );

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  return (
    <WorkspaceShell
      session={session}
      role="parent"
      currentNav="dashboard"
      eyebrow="Family Portal"
      title="A clearer view of your children's school life"
      description="Follow attendance, fee status, communication, and early performance signals from one dependable family dashboard."
      actions={
        <>
          <Button variant="secondary">Contact school</Button>
          <Button variant="primary">Pay fees</Button>
        </>
      }
    >
      {loading ? (
        <div className="flex min-h-[320px] items-center justify-center">
          <div className="flex items-center gap-3 rounded-full bg-slate-950 px-5 py-3 text-white">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm font-medium">Loading family portal...</span>
          </div>
        </div>
      ) : error ? (
        <Alert variant="error">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5" />
            <div>
              <p className="font-medium">Parent dashboard error</p>
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

          <SectionCard title="Children overview" description="Switch between linked learner profiles without leaving the flow.">
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {children.map((child) => (
                <button
                  key={child.id}
                  type="button"
                  onClick={() => setSelectedChildId(child.id)}
                  className={`rounded-[22px] border px-4 py-4 text-left transition ${
                    selectedChild?.id === child.id
                      ? 'border-slate-950 bg-slate-950 text-white'
                      : 'border-slate-200 bg-slate-50 text-slate-950 hover:border-slate-300'
                  }`}
                >
                  <p className="font-medium">
                    {child.first_name} {child.last_name}
                  </p>
                  <p className={`mt-1 text-sm ${selectedChild?.id === child.id ? 'text-white/70' : 'text-slate-500'}`}>
                    {child.classroom || 'No classroom'}  {child.admission_number}
                  </p>
                  <p className={`mt-3 text-xs uppercase tracking-[0.14em] ${selectedChild?.id === child.id ? 'text-white/70' : 'text-slate-500'}`}>
                    {titleize(child.status)}
                  </p>
                </button>
              ))}
            </div>
          </SectionCard>

          {selectedChild ? (
            <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
              <div className="space-y-6">
                {selectedFee ? (
                  <SectionCard
                    title={`Fee position for ${selectedChild.first_name}`}
                    description="A simple, current picture of due amounts, payments, and the remaining balance."
                  >
                    <div className="rounded-[24px] bg-slate-950 p-5 text-white">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm text-white/70">Current balance</p>
                          <p className="mt-2 text-4xl font-semibold">{formatCurrency(selectedFee.balance || 0, 'NGN')}</p>
                        </div>
                        <FeeStatus fee={selectedFee} />
                      </div>
                      <div className="mt-5 grid gap-3 md:grid-cols-2">
                        <div className="rounded-[20px] bg-white/10 px-4 py-4">
                          <p className="text-sm text-white/70">Total due</p>
                          <p className="mt-2 text-2xl font-semibold">{formatCurrency(selectedFee.total_due || 0, 'NGN')}</p>
                        </div>
                        <div className="rounded-[20px] bg-white/10 px-4 py-4">
                          <p className="text-sm text-white/70">Amount paid</p>
                          <p className="mt-2 text-2xl font-semibold">{formatCurrency(selectedFee.amount_paid || 0, 'NGN')}</p>
                        </div>
                      </div>
                    </div>
                    {(selectedFee.balance || 0) > 0 ? (
                      <Alert variant="warning" className="mt-4">
                        <div className="flex items-start gap-3">
                          <AlertCircle className="mt-0.5 h-5 w-5" />
                          <div>
                            <p className="font-medium">Outstanding fee reminder</p>
                            <p className="mt-1 text-sm">
                              A balance remains on this learner account. Keeping it current helps avoid service interruptions.
                            </p>
                          </div>
                        </div>
                      </Alert>
                    ) : null}
                  </SectionCard>
                ) : null}

                {selectedAttendance ? (
                  <SectionCard
                    title="Attendance health"
                    description="See how regularly this child is showing up and where attention may be needed."
                  >
                    <div className="grid gap-4 md:grid-cols-[0.95fr_1.05fr]">
                      <div className="rounded-[24px] bg-slate-50 p-5">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-slate-500">Attendance rate</p>
                            <p className="mt-2 text-4xl font-semibold text-slate-950">
                              {Math.round(selectedAttendance.attendance_percentage || 0)}%
                            </p>
                          </div>
                          <CalendarDays className="h-8 w-8 text-slate-400" />
                        </div>
                        <div className="mt-5 h-2 rounded-full bg-slate-200">
                          <div
                            className="h-2 rounded-full bg-emerald-500"
                            style={{ width: `${Math.min(selectedAttendance.attendance_percentage || 0, 100)}%` }}
                          />
                        </div>
                      </div>
                      <div className="grid gap-3 sm:grid-cols-3">
                        {[
                          ['Present', selectedAttendance.present_days || 0],
                          ['Late', selectedAttendance.late_days || 0],
                          ['Absent', selectedAttendance.absent_days || 0],
                        ].map(([label, value]) => (
                          <div key={label} className="rounded-[22px] border border-slate-200 px-4 py-4">
                            <p className="text-sm text-slate-500">{label}</p>
                            <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </SectionCard>
                ) : null}
              </div>

              <div className="space-y-6">
                {selectedInsight ? (
                  <SectionCard
                    title="Learning attention signal"
                    description="A family-friendly reading of how this child's momentum looks right now."
                  >
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-slate-600">Overall signal</span>
                        <RiskBadge
                          level={
                            (selectedInsight.attendance_risk || 0) > 0.65 || (selectedInsight.performance_risk || 0) > 0.65
                              ? 'HIGH'
                              : (selectedInsight.attendance_risk || 0) > 0.35 || (selectedInsight.performance_risk || 0) > 0.35
                                ? 'MEDIUM'
                                : 'LOW'
                          }
                        />
                      </div>
                      <div className="space-y-3 rounded-[22px] bg-slate-50 p-4">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-600">Attendance risk</span>
                          <span className="font-semibold text-slate-950">
                            {Math.round((selectedInsight.attendance_risk || 0) * 100)}%
                          </span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-slate-600">Performance risk</span>
                          <span className="font-semibold text-slate-950">
                            {Math.round((selectedInsight.performance_risk || 0) * 100)}%
                          </span>
                        </div>
                      </div>
                      {Array.isArray(selectedInsight.flagged_subjects) && selectedInsight.flagged_subjects.length > 0 ? (
                        <div>
                          <p className="text-sm font-medium text-slate-950">Subjects worth checking in on</p>
                          <div className="mt-3 flex flex-wrap gap-2">
                            {selectedInsight.flagged_subjects.map((subject) => (
                              <Badge key={subject} variant="warning">
                                {subject}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      ) : null}
                    </div>
                  </SectionCard>
                ) : null}

                <SectionCard title="Communication" description="Stay ahead of school updates and family follow-up.">
                  <div className="rounded-[22px] bg-slate-50 px-4 py-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-slate-500">Unread messages</p>
                        <p className="mt-2 text-3xl font-semibold text-slate-950">{messages.unread_count || 0}</p>
                      </div>
                      <ShieldCheck className="h-8 w-8 text-slate-400" />
                    </div>
                  </div>
                  <div className="mt-4 space-y-3">
                    <Button fullWidth variant="secondary">
                      <MessageSquare className="h-4 w-4" />
                      Open conversations
                    </Button>
                    <Button fullWidth variant="secondary">
                      <CreditCard className="h-4 w-4" />
                      Review fee history
                    </Button>
                  </div>
                </SectionCard>

                {/* Messaging Section */}
                <SectionCard id="messaging" title="Messages & Updates" description="Direct communication with teachers and school.">
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-sm text-slate-600"> Receive school announcements, message teachers, and stay informed about your child's progress.</p>
                    <button className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
                      View messages
                    </button>
                  </div>
                </SectionCard>
              </div>
            </div>
          ) : null}
        </div>
      )}
    </WorkspaceShell>
  );
};
