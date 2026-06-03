import React from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

/**
 * Chart Colors Palette
 */
const CHART_COLORS = {
  primary: '#1e5eff',
  secondary: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#06b6d4',
  slate: '#64748b',
};

/**
 * Enrollment Trend Chart - Shows student enrollment over time
 */
export const EnrollmentTrendChart = ({ data = [], height = 300 }) => {
  if (!data || data.length === 0) {
    return (
      <div
        className="w-full bg-slate-50 rounded-lg p-8 text-center text-slate-500"
        role="region"
        aria-label="Enrollment trend chart"
      >
        No enrollment data available
      </div>
    );
  }

  return (
    <div
      role="region"
      aria-label="Enrollment trend chart showing student count over time"
      className="w-full"
    >
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorEnrollment" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.8} />
              <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: `1px solid ${CHART_COLORS.primary}`,
              borderRadius: '8px',
            }}
          />
          <Area
            type="monotone"
            dataKey="students"
            stroke={CHART_COLORS.primary}
            fillOpacity={1}
            fill="url(#colorEnrollment)"
            name="Students"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Attendance Overview Chart - Shows attendance percentage over time
 */
export const AttendanceChart = ({ data = [], height = 300 }) => {
  if (!data || data.length === 0) {
    return (
      <div
        className="w-full bg-slate-50 rounded-lg p-8 text-center text-slate-500"
        role="region"
        aria-label="Attendance chart"
      >
        No attendance data available
      </div>
    );
  }

  return (
    <div
      role="region"
      aria-label="Attendance percentage chart by class"
      className="w-full"
    >
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="class" />
          <YAxis label={{ value: 'Percentage', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value) => `${value}%`}
            contentStyle={{
              backgroundColor: '#fff',
              border: `1px solid ${CHART_COLORS.secondary}`,
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Bar dataKey="present" fill={CHART_COLORS.secondary} name="Present %" />
          <Bar dataKey="absent" fill={CHART_COLORS.error} name="Absent %" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Revenue Trend Chart - Shows monthly revenue
 */
export const RevenueTrendChart = ({ data = [], height = 300 }) => {
  if (!data || data.length === 0) {
    return (
      <div
        className="w-full bg-slate-50 rounded-lg p-8 text-center text-slate-500"
        role="region"
        aria-label="Revenue chart"
      >
        No revenue data available
      </div>
    );
  }

  return (
    <div
      role="region"
      aria-label="Monthly revenue trend chart"
      className="w-full"
    >
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip
            formatter={(value) => `${value.toLocaleString()}`}
            contentStyle={{
              backgroundColor: '#fff',
              border: `1px solid ${CHART_COLORS.primary}`,
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="revenue"
            stroke={CHART_COLORS.primary}
            strokeWidth={2}
            dot={{ fill: CHART_COLORS.primary }}
            activeDot={{ r: 6 }}
            name="Revenue"
          />
          <Line
            type="monotone"
            dataKey="target"
            stroke={CHART_COLORS.warning}
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ fill: CHART_COLORS.warning }}
            name="Target"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Grade Distribution Chart - Shows distribution of grades
 */
export const GradeDistributionChart = ({ data = [], height = 300 }) => {
  if (!data || data.length === 0) {
    return (
      <div
        className="w-full bg-slate-50 rounded-lg p-8 text-center text-slate-500"
        role="region"
        aria-label="Grade distribution chart"
      >
        No grade data available
      </div>
    );
  }

  const GRADE_COLORS = [
    CHART_COLORS.secondary, // A
    CHART_COLORS.info,       // B
    CHART_COLORS.warning,    // C
    CHART_COLORS.error,      // D
  ];

  return (
    <div
      role="region"
      aria-label="Grade distribution pie chart"
      className="w-full"
    >
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, value }) => `${name}: ${value}`}
            outerRadius={80}
            fill={CHART_COLORS.primary}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={GRADE_COLORS[index % GRADE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `${value} students`} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

/**
 * Performance Matrix Chart - Shows student performance levels
 */
export const PerformanceMatrixChart = ({ data = [], height = 300 }) => {
  if (!data || data.length === 0) {
    return (
      <div
        className="w-full bg-slate-50 rounded-lg p-8 text-center text-slate-500"
        role="region"
        aria-label="Performance matrix chart"
      >
        No performance data available
      </div>
    );
  }

  return (
    <div
      role="region"
      aria-label="Student performance levels chart"
      className="w-full"
    >
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="category" />
          <YAxis />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: `1px solid ${CHART_COLORS.primary}`,
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Bar dataKey="excellent" fill={CHART_COLORS.secondary} name="Excellent" />
          <Bar dataKey="good" fill={CHART_COLORS.info} name="Good" />
          <Bar dataKey="average" fill={CHART_COLORS.warning} name="Average" />
          <Bar dataKey="poor" fill={CHART_COLORS.error} name="Needs Support" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
