import React from 'react';
import { TrendingUp, AlertTriangle, Sparkles, CheckCircle2 } from 'lucide-react';

/**
 * Smart Insight Cards
 * AI-powered insights that surface actionable intelligence
 */

export const SmartInsight = ({ type = 'info', title, message, action, confidence = null }) => {
  const variants = {
    success: {
      bg: 'bg-green-50 dark:bg-green-950/30',
      border: 'border-green-200 dark:border-green-800 border-l-4 border-l-green-500',
      title: 'text-green-900 dark:text-green-100',
      text: 'text-green-700 dark:text-green-200',
      icon: CheckCircle2,
      accentColor: 'text-green-500',
    },
    warning: {
      bg: 'bg-amber-50 dark:bg-amber-950/30',
      border: 'border-amber-200 dark:border-amber-800 border-l-4 border-l-amber-500',
      title: 'text-amber-900 dark:text-amber-100',
      text: 'text-amber-700 dark:text-amber-200',
      icon: AlertTriangle,
      accentColor: 'text-amber-500',
    },
    info: {
      bg: 'bg-blue-50 dark:bg-blue-950/30',
      border: 'border-blue-200 dark:border-blue-800 border-l-4 border-l-blue-500',
      title: 'text-blue-900 dark:text-blue-100',
      text: 'text-blue-700 dark:text-blue-200',
      icon: Sparkles,
      accentColor: 'text-blue-500',
    },
    trending: {
      bg: 'bg-purple-50 dark:bg-purple-950/30',
      border: 'border-purple-200 dark:border-purple-800 border-l-4 border-l-purple-500',
      title: 'text-purple-900 dark:text-purple-100',
      text: 'text-purple-700 dark:text-purple-200',
      icon: TrendingUp,
      accentColor: 'text-purple-500',
    },
  };

  const variant = variants[type] || variants.info;
  const Icon = variant.icon;

  return (
    <div className={`${variant.bg} ${variant.border} rounded-lg p-4 transition-all duration-300 hover:shadow-md`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex gap-3 flex-1">
          <Icon className={`h-5 w-5 ${variant.accentColor} flex-shrink-0 mt-0.5`} />
          <div className="flex-1">
            <p className={`font-semibold text-sm ${variant.title}`}>{title}</p>
            <p className={`text-sm mt-1 ${variant.text}`}>{message}</p>
            {action && (
              <button className={`text-sm font-medium mt-2 underline ${variant.accentColor} hover:no-underline`}>
                {action}
              </button>
            )}
          </div>
        </div>
        {confidence && (
          <div className="text-right flex-shrink-0">
            <div className={`text-xs font-medium ${variant.accentColor}`}>
              {Math.round(confidence * 100)}% confident
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export const InsightGrid = ({ insights = [] }) => (
  <div className="space-y-3">
    {insights.length > 0 ? (
      insights.map((insight, idx) => (
        <SmartInsight
          key={idx}
          type={insight.type}
          title={insight.title}
          message={insight.message}
          action={insight.action}
          confidence={insight.confidence}
        />
      ))
    ) : (
      <div className="text-sm text-slate-500 text-center py-8">No insights available yet</div>
    )}
  </div>
);

/**
 * Predefined insight generators for common patterns
 */
export const generateInsights = (dashboardData, role) => {
  const insights = [];

  if (role === 'admin' && dashboardData) {
    const stats = dashboardData.statistics || {};
    const finance = dashboardData.finance || {};

    // Collection trend insight
    if (finance.collection_percentage > 80) {
      insights.push({
        type: 'success',
        title: 'Strong Collection Performance',
        message: `Collections at ${finance.collection_percentage}% - performing above average`,
        action: 'View trend',
        confidence: 0.92,
      });
    } else if (finance.collection_percentage < 50) {
      insights.push({
        type: 'warning',
        title: 'Low Collection Rate',
        message: `Only ${finance.collection_percentage}% collected - consider payment reminders`,
        action: 'Send reminders',
        confidence: 0.85,
      });
    }

    // At-risk students insight
    if (stats.at_risk_students > 5) {
      insights.push({
        type: 'warning',
        title: 'Students Needing Attention',
        message: `${stats.at_risk_students} students flagged for intervention - prioritize follow-up this week`,
        action: 'View at-risk list',
        confidence: 0.89,
      });
    }

    // Growth insight
    if (stats.total_students > 100) {
      insights.push({
        type: 'trending',
        title: 'Growing Enrollment',
        message: `${stats.total_students} active learners - consider resource planning`,
        action: null,
        confidence: 0.78,
      });
    }
  }

  if (role === 'bursar' && dashboardData) {
    const financial = dashboardData.financial_summary || {};
    
    // Outstanding balance insight
    if ((financial.total_due || 0) > financial.total_paid) {
      const outstanding = (financial.total_due || 0) - (financial.total_paid || 0);
      insights.push({
        type: 'info',
        title: 'Payment Opportunity',
        message: `Outstanding balance: ₦${outstanding.toLocaleString()} - send collection reminder`,
        action: 'Email families',
        confidence: 0.81,
      });
    }

    // Collection rate insight
    if (financial.total_paid > 0) {
      const rate = ((financial.total_paid / financial.total_due) * 100).toFixed(0);
      if (rate > 75) {
        insights.push({
          type: 'success',
          title: 'Excellent Collection Rate',
          message: `${rate}% of fees collected - well ahead of target`,
          action: null,
          confidence: 0.88,
        });
      }
    }
  }

  if (role === 'teacher' && dashboardData) {
    const summary = dashboardData.summary || {};

    // Class performance insight
    if (summary.at_risk_students > 3) {
      insights.push({
        type: 'warning',
        title: 'Class Performance Alert',
        message: `${summary.at_risk_students} students in your classes need academic support`,
        action: 'View interventions',
        confidence: 0.84,
      });
    }

    // Attendance insight
    if (summary.average_attendance < 80) {
      insights.push({
        type: 'warning',
        title: 'Attendance Concern',
        message: `Class attendance averaging ${summary.average_attendance}% - follow up with absent students`,
        action: 'Send attendance note',
        confidence: 0.76,
      });
    }
  }

  return insights;
};
