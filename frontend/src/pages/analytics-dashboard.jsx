import React, { useEffect, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  BarChart3,
  Loader2,
  TrendingDown,
  TrendingUp,
  Users,
  Award,
  Zap,
} from 'lucide-react';

import { WorkspaceShell } from '../components/workspace-shell';
import { Alert } from '../components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { getCurrentUser, getStoredSession } from '../lib/django';
import { apiClient } from '../lib/api-client';
import { useAuth } from '../lib/hooks';

const StatBox = ({ icon: Icon, label, value, detail, trend }) => (
  <Card>
    <CardContent className="pt-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-600">{label}</p>
          <p className="mt-2 text-3xl font-bold text-slate-950">{value}</p>
          {detail && <p className="mt-1 text-xs text-slate-500">{detail}</p>}
        </div>
        <div className="rounded-lg bg-slate-100 p-3">
          <Icon className="h-6 w-6 text-slate-600" />
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center gap-1">
          {trend.direction === 'up' ? (
            <TrendingUp className="h-4 w-4 text-emerald-600" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-600" />
          )}
          <span className={trend.direction === 'up' ? 'text-emerald-600' : 'text-red-600'}>
            {trend.text}
          </span>
        </div>
      )}
    </CardContent>
  </Card>
);

export const AnalyticsDashboardPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [session, setSession] = useState(() => getStoredSession());
  const [data, setData] = useState(null);
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
          setError('Unable to determine your role.');
          return;
        }

        // Only admins can view advanced analytics
        if (!['admin', 'superadmin'].includes(activeSession.role)) {
          navigate('/app/dashboard');
          return;
        }

        setSession(activeSession);

        // Fetch analytics data
        const response = await apiClient.get('/api/analytics/advanced-analytics/');
        setData(response.data);
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.response?.data?.detail ||
          'Unable to load analytics right now.'
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isAuthenticated, navigate]);

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  return (
    <WorkspaceShell
      session={session}
      role={session?.role || 'admin'}
      currentNav="analytics"
      eyebrow="Analytics & Insights"
      title="Advanced Analytics Dashboard"
      description="AI-powered insights, performance metrics, and school-wide analytics."
    >
      {loading ? (
        <div className="flex min-h-[280px] items-center justify-center">
          <div className="flex items-center gap-3 rounded-full bg-slate-950 px-5 py-3 text-white shadow-sm">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm font-medium">Loading analytics...</span>
          </div>
        </div>
      ) : error ? (
        <Alert variant="error">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5" />
            <div>
              <p className="font-medium">Analytics error</p>
              <p className="mt-1 text-sm">{error}</p>
            </div>
          </div>
        </Alert>
      ) : data ? (
        <div className="space-y-8">
          {/* Overview Stats */}
          <div>
            <h2 className="mb-4 text-lg font-semibold text-slate-950">Overview</h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <StatBox
                icon={Users}
                label={session?.role === 'superadmin' ? 'Total Students' : 'School Students'}
                value={data.students?.total || 0}
                detail="Across the platform"
              />
              <StatBox
                icon={AlertCircle}
                label="Students At Risk"
                value={data.students?.at_risk || 0}
                detail="Requiring intervention"
              />
              <StatBox
                icon={Award}
                label="Avg. Attendance"
                value={`${data.attendance?.average_rate || 0}%`}
                detail="Last 30 days"
                trend={{
                  direction: (data.attendance?.average_rate || 0) > 75 ? 'up' : 'down',
                  text: (data.attendance?.average_rate || 0) > 75 ? 'Above target' : 'Below target',
                }}
              />
              <StatBox
                icon={Zap}
                label="Avg. Performance"
                value={`${data.performance?.average_score || 0}%`}
                detail={`${data.performance?.total_exams || 0} assessments`}
              />
            </div>
          </div>

          {/* AI Risk Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>AI Risk Analysis</CardTitle>
              <CardDescription>Attendance and performance risk scores (0-1 scale)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-slate-950">Attendance Risk</p>
                    <div className="mt-2 h-3 rounded-full bg-slate-200">
                      <div
                        className="h-3 rounded-full bg-red-500"
                        style={{
                          width: `${(data.risk_analysis?.avg_attendance_risk || 0) * 100}%`,
                        }}
                      />
                    </div>
                    <p className="mt-2 text-sm text-slate-600">
                      Score: {data.risk_analysis?.avg_attendance_risk || 0}/1.0
                    </p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-slate-950">Performance Risk</p>
                    <div className="mt-2 h-3 rounded-full bg-slate-200">
                      <div
                        className="h-3 rounded-full bg-yellow-500"
                        style={{
                          width: `${(data.risk_analysis?.avg_performance_risk || 0) * 100}%`,
                        }}
                      />
                    </div>
                    <p className="mt-2 text-sm text-slate-600">
                      Score: {data.risk_analysis?.avg_performance_risk || 0}/1.0
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Finance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle>Finance & Collections</CardTitle>
              <CardDescription>Fee collection and outstanding balances</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-3">
                <div>
                  <p className="text-sm text-slate-600">Total Due</p>
                  <p className="mt-2 text-2xl font-bold text-slate-950">
                    {Number(data.finance?.total_due || 0).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-slate-600">Total Collected</p>
                  <p className="mt-2 text-2xl font-bold text-emerald-600">
                    {Number(data.finance?.total_collected || 0).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-slate-600">Collection Rate</p>
                  <p className="mt-2 text-2xl font-bold text-slate-950">
                    {data.finance?.collection_rate || 0}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                AI System Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-lg bg-emerald-50 p-4">
                  <span className="text-sm font-medium text-emerald-900">AI Risk Calculation</span>
                  <span className="rounded-full bg-emerald-200 px-3 py-1 text-xs font-semibold text-emerald-700">
                    Active
                  </span>
                </div>
                <p className="text-sm text-slate-600">
                  AI insights are calculated automatically. Run{' '}
                  <code className="rounded bg-slate-100 px-2 py-1 text-xs">
                    python manage.py calculate_ai_insights
                  </code>{' '}
                  to refresh data.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </WorkspaceShell>
  );
};
