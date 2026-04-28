/**
 * Skeleton Loaders
 * Reusable loading placeholders for better UX during data fetching
 * Uses CSS animations for smooth, polished feel
 */

import React from 'react';

/**
 * Generic Skeleton Placeholder
 * Shimmer animation that looks like content loading
 */
export const Skeleton = ({
  className = '',
  width = 'w-full',
  height = 'h-4',
  variant = 'default',
}) => {
  const baseClasses = 'animate-pulse bg-slate-200 rounded';
  const variantClasses = {
    default: 'bg-slate-200',
    circle: 'rounded-full',
  };

  return (
    <div
      className={`${baseClasses} ${width} ${height} ${variantClasses[variant]} ${className}`}
      style={{
        animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }}
    />
  );
};

/**
 * Stat Card Skeleton (3 columns)
 * Mimics the StatCard layout used in dashboards
 */
export const StatCardSkeleton = () => (
  <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <Skeleton width="w-24" height="h-4" className="mb-3" />
        <Skeleton width="w-32" height="h-6" />
      </div>
      <Skeleton width="w-12" height="h-12" variant="circle" />
    </div>
  </div>
);

/**
 * Multiple Stat Cards Skeleton
 */
export const StatCardsGridSkeleton = ({ count = 4 }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    {Array.from({ length: count }).map((_, i) => (
      <StatCardSkeleton key={i} />
    ))}
  </div>
);

/**
 * Table Row Skeleton
 * Mimics a table row with multiple columns
 */
export const TableRowSkeleton = ({ columnCount = 5 }) => (
  <tr className="border-b border-slate-200">
    {Array.from({ length: columnCount }).map((_, i) => (
      <td key={i} className="px-6 py-4">
        <Skeleton width="w-full" height="h-4" />
      </td>
    ))}
  </tr>
);

/**
 * Table Skeleton
 * Mimics a table with header and rows
 */
export const TableSkeleton = ({
  rowCount = 5,
  columnCount = 5,
  hasHeader = true,
}) => (
  <div className="overflow-x-auto border border-slate-200 rounded-lg">
    <table className="w-full">
      {hasHeader && (
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr>
            {Array.from({ length: columnCount }).map((_, i) => (
              <th key={i} className="px-6 py-4 text-left">
                <Skeleton width="w-20" height="h-4" />
              </th>
            ))}
          </tr>
        </thead>
      )}
      <tbody>
        {Array.from({ length: rowCount }).map((_, i) => (
          <TableRowSkeleton key={i} columnCount={columnCount} />
        ))}
      </tbody>
    </table>
  </div>
);

/**
 * Card Skeleton
 * Mimics a card with header, content, and footer
 */
export const CardSkeleton = ({
  hasHeader = true,
  hasFooter = true,
  contentLines = 3,
}) => (
  <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
    {hasHeader && (
      <div className="bg-slate-50 border-b border-slate-200 px-6 py-4">
        <Skeleton width="w-32" height="h-5" />
      </div>
    )}

    <div className="px-6 py-4 space-y-3">
      {Array.from({ length: contentLines }).map((_, i) => (
        <Skeleton
          key={i}
          width={i === contentLines - 1 ? 'w-3/4' : 'w-full'}
          height="h-4"
        />
      ))}
    </div>

    {hasFooter && (
      <div className="bg-slate-50 border-t border-slate-200 px-6 py-4 flex gap-3">
        <Skeleton width="w-20" height="h-8" />
        <Skeleton width="w-20" height="h-8" />
      </div>
    )}
  </div>
);

/**
 * Form Input Skeleton
 */
export const FormInputSkeleton = ({ label = true }) => (
  <div>
    {label && <Skeleton width="w-24" height="h-4" className="mb-2" />}
    <Skeleton width="w-full" height="h-10" />
  </div>
);

/**
 * Form Skeleton
 * Mimics a form with multiple inputs
 */
export const FormSkeleton = ({ fieldCount = 4 }) => (
  <div className="space-y-4">
    {Array.from({ length: fieldCount }).map((_, i) => (
      <FormInputSkeleton key={i} />
    ))}
    <Skeleton width="w-full" height="h-10" className="mt-6" />
  </div>
);

/**
 * List Item Skeleton
 */
export const ListItemSkeleton = () => (
  <div className="flex items-center gap-4 p-4 border-b border-slate-200">
    <Skeleton width="w-12" height="h-12" variant="circle" />
    <div className="flex-1 space-y-2">
      <Skeleton width="w-32" height="h-4" />
      <Skeleton width="w-48" height="h-3" />
    </div>
  </div>
);

/**
 * List Skeleton
 * Mimics a list with multiple items
 */
export const ListSkeleton = ({ itemCount = 5 }) => (
  <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
    {Array.from({ length: itemCount }).map((_, i) => (
      <ListItemSkeleton key={i} />
    ))}
  </div>
);

/**
 * Dashboard Header Skeleton
 * Mimics header with title and breadcrumbs
 */
export const DashboardHeaderSkeleton = () => (
  <div className="mb-8">
    <Skeleton width="w-48" height="h-3" className="mb-2" />
    <Skeleton width="w-64" height="h-6" className="mb-4" />
    <Skeleton width="w-80" height="h-4" />
  </div>
);

/**
 * Full Dashboard Skeleton
 * Combines all elements for a complete page skeleton
 */
export const DashboardSkeleton = () => (
  <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-white py-12">
    <div className="container mx-auto px-4 md:px-6 space-y-8">
      <DashboardHeaderSkeleton />
      <StatCardsGridSkeleton count={4} />
      <CardSkeleton contentLines={5} />
      <CardSkeleton contentLines={5} />
    </div>
  </div>
);

/**
 * Wrapper component to show skeleton when loading
 */
export const WithSkeleton = ({
  isLoading,
  skeleton = <DashboardSkeleton />,
  children,
}) => {
  if (isLoading) {
    return skeleton;
  }
  return children;
};

export default {
  Skeleton,
  StatCardSkeleton,
  StatCardsGridSkeleton,
  TableRowSkeleton,
  TableSkeleton,
  CardSkeleton,
  FormInputSkeleton,
  FormSkeleton,
  ListItemSkeleton,
  ListSkeleton,
  DashboardHeaderSkeleton,
  DashboardSkeleton,
  WithSkeleton,
};
