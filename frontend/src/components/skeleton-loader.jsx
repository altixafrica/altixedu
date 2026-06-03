import React from 'react';

/**
 * Skeleton Loader Components
 * Premium loading states instead of spinners
 */

export const SkeletonCard = ({ className = '' }) => (
  <div className={`animate-pulse rounded-lg border border-slate-200 bg-slate-50 p-5 ${className}`}>
    <div className="space-y-3">
      <div className="h-4 w-1/3 rounded bg-slate-300" />
      <div className="h-8 w-2/3 rounded bg-slate-300" />
      <div className="h-3 w-1/2 rounded bg-slate-300" />
    </div>
  </div>
);

export const SkeletonChart = ({ className = '' }) => (
  <div className={`rounded-lg border border-slate-200 bg-slate-50 p-6 ${className}`}>
    <div className="space-y-4">
      <div className="h-4 w-1/4 rounded bg-slate-300" />
      <div className="flex gap-2">
        {[...Array(12)].map((_, i) => (
          <div key={i} className="flex-1">
            <div className={`animate-pulse rounded bg-slate-300 ${i % 3 === 0 ? 'h-32' : i % 3 === 1 ? 'h-24' : 'h-28'}`} />
          </div>
        ))}
      </div>
    </div>
  </div>
);

export const SkeletonTable = ({ rows = 5, className = '' }) => (
  <div className={`space-y-3 ${className}`}>
    {[...Array(rows)].map((_, i) => (
      <div key={i} className="flex gap-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
        <div className="h-4 w-1/4 animate-pulse rounded bg-slate-300" />
        <div className="h-4 w-1/3 animate-pulse rounded bg-slate-300" />
        <div className="h-4 w-1/4 animate-pulse rounded bg-slate-300" />
      </div>
    ))}
  </div>
);

export const SkeletonGrid = ({ columns = 4, className = '' }) => (
  <div className={`grid gap-4 ${`xl:grid-cols-${columns}`} ${className}`}>
    {[...Array(columns)].map((_, i) => (
      <SkeletonCard key={i} />
    ))}
  </div>
);
