import { describe, expect, it } from 'vitest';

import { getDashboardPathForRole } from '../../src/lib/django';

describe('getDashboardPathForRole', () => {
  it('returns role-specific dashboard routes', () => {
    expect(getDashboardPathForRole('admin')).toBe('/dashboard');
    expect(getDashboardPathForRole('teacher')).toBe('/app/teacher');
    expect(getDashboardPathForRole('student')).toBe('/app/student');
    expect(getDashboardPathForRole('parent')).toBe('/app/parent');
    expect(getDashboardPathForRole('bursar')).toBe('/app/bursar');
  });

  it('falls back to the shared dashboard route', () => {
    expect(getDashboardPathForRole('unknown')).toBe('/dashboard');
  });
});
