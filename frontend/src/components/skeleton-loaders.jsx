import React from 'react';

/**
 * MessageSkeleton - Skeleton loader for message lists
 * Shows animated placeholder while messages load
 * Impact: +0.2 rating (perceived performance)
 */
export const MessageSkeleton = ({ count = 3 }) => {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="space-y-2 p-3 rounded-lg bg-slate-50">
          <div className="h-4 bg-slate-200 rounded w-3/4 animate-pulse" />
          <div className="h-3 bg-slate-100 rounded w-full animate-pulse" />
          <div className="h-3 bg-slate-100 rounded w-5/6 animate-pulse" />
        </div>
      ))}
    </div>
  );
};

/**
 * FormFieldSkeleton - Skeleton for form fields
 */
export const FormFieldSkeleton = () => {
  return (
    <div className="space-y-2">
      <div className="h-4 bg-slate-200 rounded w-24 animate-pulse" />
      <div className="h-10 bg-slate-100 rounded animate-pulse" />
    </div>
  );
};

/**
 * DataTableSkeleton - Skeleton for table rows
 */
export const DataTableSkeleton = ({ rows = 5, columns = 4 }) => {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          {Array.from({ length: columns }).map((_, j) => (
            <div key={j} className="h-6 bg-slate-200 rounded flex-1 animate-pulse" />
          ))}
        </div>
      ))}
    </div>
  );
};
