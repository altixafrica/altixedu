import React, { useEffect, useMemo, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  BookOpen,
  CalendarDays,
  ClipboardList,
  Loader2,
  MessageSquare,
  Sparkles,
  TrendingUp,
} from 'lucide-react';

import { WorkspaceShell } from '../components/workspace-shell';
import { StatCard } from '../components/stat-card';
import { Alert, Badge } from '../components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { getCurrentUser, getStoredSession } from '../lib/django';
import { getDashboardByRole } from '../lib/api-service';
import { formatDate, titleize } from '../lib/format';
import { useAuth } from '../lib/hooks';

const RiskBadge = ({ level }) => {
  const variants = {
    LOW: 'success',
    MEDIUM: 'warning',
    HIGH: 'error',
  };

  return <Badge variant={variants[level] || 'default'}>{level}</Badge>;
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

export const StudentDashboardPage = () => {
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

        if (activeSession.role !== 'student') {
          navigate(`/app/${activeSession.role}`);
          return;
        }

        setSession(activeSession);
        setDashboardData(await getDashboardByRole.student());
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.response?.data?.detail ||
          'Unable to load the student workspace right now.'
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isAuthenticated, navigate]);

  const summary = dashboardData?.summary || {};
  const student = dashboardData?.student || {};
  const subjects = dashboardData?.subjects || [];
  const results = dashboardData?.results || [];
  const attendance = dashboardData?.attendance || [];
  const aiInsight = dashboardData?.ai_insight || {};

  const statCards = useMemo(
    () => [
      {
        label: 'Attendance',
        value: `${Math.round(summary.attendance_percentage || 0)}%`,
        detail: 'Presence over the last 30 days',
        icon: <CalendarDays className="h-5 w-5" />,
      },
      {
        label: 'Average grade',
        value: Number(summary.average_grade || 0).toFixed(1),
        detail: 'Recent assessed performance',
        icon: <TrendingUp className="h-5 w-5" />,
        tone: 'dark',
      },
      {
        label: 'Subjects',
        value: summary.subjects_count || 0,
        detail: 'Current classroom load',
        icon: <BookOpen className="h-5 w-5" />,
      },
      {
        label: 'Unread messages',
        value: summary.unread_messages || 0,
        detail: 'School and teacher communication',
        icon: <MessageSquare className="h-5 w-5" />,
      },
    ],
    [summary]
  );

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  return (
    <WorkspaceShell
      session={session}
      role="student"
      currentNav="dashboard"
      eyebrow="Student Workspace"
      title={`Progress overview for ${session?.user?.first_name || 'student'}`}
      description="A calmer daily view of learning momentum, attendance, performance signals, and the school updates that matter."
    >
      {loading ? (
        <div className="flex min-h-[320px] items-center justify-center">
          <div className="flex items-center gap-3 rounded-full bg-slate-950 px-5 py-3 text-white">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm font-medium">Loading student workspace...</span>
          </div>
        </div>
      ) : error ? (
        <Alert variant="error">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5" />
            <div>
              <p className="font-medium">Student dashboard error</p>
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

          {aiInsight.risk_level && aiInsight.risk_level !== 'LOW' ? (
            <Alert variant={aiInsight.risk_level === 'HIGH' ? 'error' : 'warning'}>
              <div className="flex items-start gap-3">
                <Sparkles className="mt-0.5 h-5 w-5" />
                <div>
                  <p className="font-medium">Study attention signal</p>
                  <p className="mt-1 text-sm leading-6">
                    {aiInsight.risk_level === 'HIGH'
                      ? 'Your recent attendance or assessment pattern needs immediate support from teachers or guardians.'
                      : 'You are slightly below your recent trend. A tighter study rhythm this week should help.'}
                  </p>
                </div>
              </div>
            </Alert>
          ) : null}

          <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <div className="space-y-6">
              <SectionCard
                title="Academic snapshot"
                description={`${student.classroom || 'No classroom assigned'} / ${student.admission_number || 'No admission number yet'}`}
              >
                <div className="grid gap-4 md:grid-cols-2">
                  {subjects.length > 0 ? (
                    subjects.map((subject) => (
                      <div key={subject.id} className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                        <p className="font-medium text-slate-950">{subject.name}</p>
                        <p className="mt-1 text-sm text-slate-500">{subject.code}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500">No subjects are assigned yet.</p>
                  )}
                </div>
              </SectionCard>

              <SectionCard title="Recent results" description="Latest assessed work and exam records.">
                <div className="space-y-3">
                  {results.length > 0 ? (
                    results.slice(0, 8).map((result) => (
                      <div
                        key={result.id}
                        className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3"
                      >
                        <div>
                          <p className="font-medium text-slate-950">{result.subject_name}</p>
                          <p className="mt-1 text-sm text-slate-500">{result.exam_name}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-semibold text-slate-950">{result.score}</p>
                          <p className="mt-1 text-xs text-slate-500">{formatDate(result.recorded_at)}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-500">No results are available yet.</p>
                  )}
                </div>
              </SectionCard>
            </div>

            <div className="space-y-6">
              <SectionCard title="Attendance trend" description="Last 30 days of classroom presence.">
                <div className="rounded-lg bg-slate-950 p-5 text-white">
                  <div className="flex items-end justify-between gap-4">
                    <div>
                      <p className="text-sm text-white/70">Attendance rate</p>
                      <p className="mt-2 text-4xl font-semibold">
                        {Math.round(summary.attendance_percentage || 0)}%
                      </p>
                    </div>
                    <CalendarDays className="h-8 w-8 text-white/80" />
                  </div>
                  <div className="mt-5 h-2 rounded-full bg-white/15">
                    <div
                      className="h-2 rounded-full bg-emerald-400"
                      style={{ width: `${Math.min(summary.attendance_percentage || 0, 100)}%` }}
                    />
                  </div>
                </div>
                <div className="grid gap-3 sm:grid-cols-3">
                  {[
                    ['Present', summary.present_days || 0],
                    ['Absent', summary.absent_days || 0],
                    ['Late', summary.late_days || 0],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-lg bg-slate-50 px-4 py-3">
                      <p className="text-sm text-slate-500">{label}</p>
                      <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
                    </div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard title="Performance signal" description="AI-assisted study attention summary.">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600">Risk level</span>
                    <RiskBadge level={aiInsight.risk_level || 'LOW'} />
                  </div>
                  <div className="space-y-3 rounded-lg bg-slate-50 p-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-600">Attendance risk</span>
                      <span className="font-semibold text-slate-950">
                        {Math.round((aiInsight.attendance_risk || 0) * 100)}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-600">Performance risk</span>
                      <span className="font-semibold text-slate-950">
                        {Math.round((aiInsight.performance_risk || 0) * 100)}%
                      </span>
                    </div>
                  </div>
                  {Array.isArray(aiInsight.flagged_subjects) && aiInsight.flagged_subjects.length > 0 ? (
                    <div>
                      <p className="text-sm font-medium text-slate-950">Subjects needing extra focus</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {aiInsight.flagged_subjects.map((subject) => (
                          <Badge key={subject} variant="warning">
                            {subject}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ) : null}
                  {Array.isArray(aiInsight.recommendations) && aiInsight.recommendations.length > 0 ? (
                    <div>
                      <p className="text-sm font-medium text-slate-950">Recommended next steps</p>
                      <div className="mt-3 space-y-2">
                        {aiInsight.recommendations.map((recommendation, index) => (
                          <div
                            key={`${recommendation}-${index}`}
                            className="flex gap-3 rounded-lg border border-slate-200 px-4 py-3"
                          >
                            <ClipboardList className="mt-0.5 h-4 w-4 text-slate-500" />
                            <p className="text-sm leading-6 text-slate-600">{recommendation}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              </SectionCard>
            </div>
          </div>

          <SectionCard title="Recent attendance records" description="Most recent school-day entries.">
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              {attendance.length > 0 ? (
                attendance.slice(0, 8).map((entry) => (
                  <div key={entry.id} className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                    <p className="text-sm text-slate-500">{formatDate(entry.date)}</p>
                    <div className="mt-3 flex items-center justify-between">
                      <p className="font-medium text-slate-950">{titleize(entry.status)}</p>
                      <Badge
                        variant={
                          entry.status === 'present'
                            ? 'success'
                            : entry.status === 'late'
                              ? 'warning'
                              : 'error'
                        }
                      >
                        {titleize(entry.status)}
                      </Badge>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No attendance entries are available yet.</p>
              )}
            </div>
          </SectionCard>
        </div>
      )}
    </WorkspaceShell>
  );
};
