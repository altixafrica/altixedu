import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';

/**
 * Dashboard Charts - Premium data visualizations
 * All using Recharts for responsive, high-performance charts
 */

const COLORS = {
  primary: '#1e5eff',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  secondary: '#64748b',
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-3 shadow-lg">
        <p className="text-sm font-medium text-slate-900">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }} className="text-xs">
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

/**
 * Fee Collection Trend Chart
 * Shows monthly fee collection trends
 */
export const FeeCollectionChart = ({ data = [] }) => {
  const defaultData = [
    { month: 'Jan', collected: 45000, outstanding: 25000 },
    { month: 'Feb', collected: 52000, outstanding: 18000 },
    { month: 'Mar', collected: 48000, outstanding: 22000 },
    { month: 'Apr', collected: 61000, outstanding: 14000 },
    { month: 'May', collected: 55000, outstanding: 20000 },
    { month: 'Jun', collected: 67000, outstanding: 8000 },
  ];

  const chartData = data.length > 0 ? data : defaultData;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Fee Collection Trend</CardTitle>
        <CardDescription>Monthly collection vs outstanding balance</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorCollected" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLORS.success} stopOpacity={0.3} />
                <stop offset="95%" stopColor={COLORS.success} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorOutstanding" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLORS.warning} stopOpacity={0.3} />
                <stop offset="95%" stopColor={COLORS.warning} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="month" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area type="monotone" dataKey="collected" stroke={COLORS.success} fillOpacity={1} fill="url(#colorCollected)" />
            <Area type="monotone" dataKey="outstanding" stroke={COLORS.warning} fillOpacity={1} fill="url(#colorOutstanding)" />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

/**
 * Student Performance Distribution
 * Shows grade distribution across the school
 */
export const StudentPerformanceChart = ({ data = [] }) => {
  const defaultData = [
    { grade: 'A', count: 24, fill: COLORS.success },
    { grade: 'B', count: 45, fill: COLORS.primary },
    { grade: 'C', count: 38, fill: '#06b6d4' },
    { grade: 'D', count: 22, fill: COLORS.warning },
    { grade: 'F', count: 8, fill: COLORS.error },
  ];

  const chartData = data.length > 0 ? data : defaultData;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Student Performance</CardTitle>
        <CardDescription>Grade distribution across all students</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="grade" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" fill={COLORS.primary} radius={[8, 8, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill || COLORS.primary} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

/**
 * Attendance Rate Over Time
 * Shows attendance trends month by month
 */
export const AttendanceChart = ({ data = [] }) => {
  const defaultData = [
    { week: 'Week 1', rate: 87 },
    { week: 'Week 2', rate: 89 },
    { week: 'Week 3', rate: 84 },
    { week: 'Week 4', rate: 91 },
    { week: 'Week 5', rate: 88 },
  ];

  const chartData = data.length > 0 ? data : defaultData;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Attendance Trend</CardTitle>
        <CardDescription>Weekly attendance rate percentage</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="week" stroke="#64748b" />
            <YAxis stroke="#64748b" domain={[0, 100]} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="rate"
              stroke={COLORS.success}
              strokeWidth={3}
              dot={{ fill: COLORS.success, r: 5 }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

/**
 * Payment Status Distribution
 * Pie chart showing paid vs partial vs unpaid
 */
export const PaymentStatusChart = ({ data = [] }) => {
  const defaultData = [
    { name: 'Paid', value: 245, fill: COLORS.success },
    { name: 'Partial', value: 89, fill: COLORS.warning },
    { name: 'Unpaid', value: 43, fill: COLORS.error },
  ];

  const chartData = data.length > 0 ? data : defaultData;

  const renderLabel = (entry) => `${entry.name}: ${entry.value}`;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Payment Status</CardTitle>
        <CardDescription>Student fee payment breakdown</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderLabel}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

/**
 * Subscription Health - For Superadmin
 * Shows MRR and subscription trends
 */
export const SubscriptionHealthChart = ({ data = [] }) => {
  const defaultData = [
    { month: 'Jan', mrr: 180000, subscribers: 18 },
    { month: 'Feb', mrr: 195000, subscribers: 19 },
    { month: 'Mar', mrr: 210000, subscribers: 21 },
    { month: 'Apr', mrr: 225000, subscribers: 23 },
    { month: 'May', mrr: 240000, subscribers: 24 },
    { month: 'Jun', mrr: 265000, subscribers: 26 },
  ];

  const chartData = data.length > 0 ? data : defaultData;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Platform Revenue Growth</CardTitle>
        <CardDescription>MRR and active subscriber trends</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="month" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="mrr"
              stroke={COLORS.primary}
              strokeWidth={2}
              dot={{ fill: COLORS.primary, r: 4 }}
              name="MRR (₦)"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="subscribers"
              stroke={COLORS.success}
              strokeWidth={2}
              dot={{ fill: COLORS.success, r: 4 }}
              name="Subscribers"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

/**
 * Ministry Performance - For Ministry Admin
 * Shows coverage, collection rate, attendance
 */
export const MinistryPerformanceChart = ({ data = [] }) => {
  const defaultData = [
    { state: 'Lagos', collection: 82, attendance: 87, target: 85 },
    { state: 'Oyo', collection: 75, attendance: 81, target: 85 },
    { state: 'Kaduna', collection: 68, attendance: 76, target: 85 },
    { state: 'Rivers', collection: 79, attendance: 84, target: 85 },
  ];

  const chartData = data.length > 0 ? data : defaultData;

  return (
    <Card>
      <CardHeader>
        <CardTitle>State Performance Comparison</CardTitle>
        <CardDescription>Collection rate vs attendance vs target</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="state" stroke="#64748b" />
            <YAxis stroke="#64748b" />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="collection" fill={COLORS.success} radius={[8, 8, 0, 0]} name="Collection %" />
            <Bar dataKey="attendance" fill={COLORS.primary} radius={[8, 8, 0, 0]} name="Attendance %" />
            <Bar dataKey="target" fill={COLORS.secondary} radius={[8, 8, 0, 0]} name="Target %" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
