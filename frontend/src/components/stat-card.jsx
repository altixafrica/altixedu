import React from 'react';

export const StatCard = ({ icon, label, value, detail, tone = 'default', className = '' }) => {
  const toneClasses = {
    default: 'bg-white border-slate-200 dark:bg-slate-800 dark:border-slate-700',
    dark: 'bg-slate-950 border-slate-950 text-white dark:bg-slate-900',
    accent: 'bg-brand-600 border-brand-600 text-white dark:bg-brand-700',
    soft: 'bg-slate-50 border-slate-200 dark:bg-slate-800 dark:border-slate-700',
  };

  return (
    <div className={`rounded-lg border p-5 shadow-sm shadow-slate-950/[0.02] dark:shadow-slate-950/30 transition-all duration-300 hover:shadow-md hover:-translate-y-1 ${toneClasses[tone] || toneClasses.default} ${className}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className={`text-sm font-medium ${tone === 'dark' || tone === 'accent' ? 'text-white/70' : 'text-slate-500 dark:text-slate-400'}`}>{label}</p>
          <p className={`mt-2 text-2xl font-semibold tracking-tight ${tone === 'dark' || tone === 'accent' ? 'text-white' : 'text-slate-950 dark:text-white'}`}>{value}</p>
          {detail ? (
            <p className={`mt-2 text-sm ${tone === 'dark' || tone === 'accent' ? 'text-white/70' : 'text-slate-600 dark:text-slate-400'}`}>{detail}</p>
          ) : null}
        </div>
        {icon && (
          <div className={`flex h-10 w-10 items-center justify-center rounded-lg transition-transform duration-200 group-hover:scale-110 ${tone === 'dark' || tone === 'accent' ? 'bg-white/10 text-white' : 'bg-slate-100 text-slate-950 dark:bg-slate-700 dark:text-slate-100'}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};
