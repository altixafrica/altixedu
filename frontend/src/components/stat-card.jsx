import React from 'react';

export const StatCard = ({ icon, label, value, detail, tone = 'default', className = '' }) => {
  const toneClasses = {
    default: 'bg-white border-slate-200',
    dark: 'bg-slate-950 border-slate-950 text-white',
    accent: 'bg-brand-600 border-brand-600 text-white',
    soft: 'bg-slate-50 border-slate-200',
  };

  return (
    <div className={`rounded-[26px] border p-6 shadow-sm shadow-slate-950/[0.03] ${toneClasses[tone] || toneClasses.default} ${className}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className={`text-sm font-medium ${tone === 'dark' || tone === 'accent' ? 'text-white/70' : 'text-slate-500'}`}>{label}</p>
          <p className={`mt-3 text-3xl font-semibold tracking-tight ${tone === 'dark' || tone === 'accent' ? 'text-white' : 'text-slate-950'}`}>{value}</p>
          {detail ? (
            <p className={`mt-2 text-sm ${tone === 'dark' || tone === 'accent' ? 'text-white/70' : 'text-slate-600'}`}>{detail}</p>
          ) : null}
        </div>
        {icon && (
          <div className={`flex h-12 w-12 items-center justify-center rounded-2xl ${tone === 'dark' || tone === 'accent' ? 'bg-white/10 text-white' : 'bg-slate-100 text-slate-950'}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};
