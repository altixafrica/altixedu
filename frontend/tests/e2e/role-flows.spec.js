import { expect, test } from '@playwright/test';

const seedSession = async (page, session) => {
  await page.addInitScript((payload) => {
    localStorage.setItem('auth_token', 'test-token');
    localStorage.setItem('user', JSON.stringify(payload.user));
    localStorage.setItem('auth_session', JSON.stringify(payload));
  }, session);
};

test.describe('login redirects by role', () => {
  const roles = [
    ['admin', '/dashboard'],
    ['teacher', '/app/teacher'],
    ['student', '/app/student'],
    ['parent', '/app/parent'],
    ['bursar', '/app/bursar'],
    ['superadmin', '/dashboard'],
    ['ministry_admin', '/dashboard'],
  ];

  for (const [role, expectedPath] of roles) {
    test(`login sends ${role} users to the correct workspace`, async ({ page }) => {
      const sessionPayload = {
        token: 'role-token',
        role,
        user: {
          id: 1,
          username: role,
          first_name: 'Role',
          last_name: 'User',
          full_name: 'Role User',
          email: `${role}@altixedu.test`,
        },
        school: role === 'superadmin' || role === 'ministry_admin' ? null : { id: 1, name: 'Atlas College' },
        ministry: role === 'ministry_admin' ? { id: 7, name: 'Ministry of Education', currency_code: 'NGN' } : null,
        permissions: [],
      };

      await page.route('**/api/auth/login/', async (route) => {
        await route.fulfill({ json: sessionPayload });
      });
      await page.route('**/api/auth/me/', async (route) => route.fulfill({ json: sessionPayload }));
      await page.route('**/api/dashboard/**', async (route) => route.fulfill({ json: {} }));
      await page.route('**/api/billing/portfolio/', async (route) => route.fulfill({ json: { summary: {}, tier_mix: [], watchlist: [], recent_transactions: [] } }));
      await page.route('**/api/government/dashboard/ministry/', async (route) => route.fulfill({ json: { results: [{}] } }));

      await page.goto('/login');
      await page.locator('#login-email').fill(`${role}@altixedu.test`);
      await page.locator('#login-password').fill('Password123!');
      await page.getByRole('button', { name: /Sign in/i }).click();
      await expect(page).toHaveURL(new RegExp(`${expectedPath.replace('/', '\\/')}$`));
    });
  }
});

test('teacher, parent, and bursar workspaces render their core panels', async ({ page }) => {
  const roleScenarios = [
    {
      role: 'teacher',
      path: '/app/teacher',
      session: {
        user: { id: 3, username: 'teacher', first_name: 'Mary', last_name: 'Ojo', full_name: 'Mary Ojo', email: 'teacher@test.dev' },
        role: 'teacher',
        school: { id: 1, name: 'Atlas College' },
        ministry: null,
        permissions: [],
      },
      dashboardPath: '**/api/dashboard/teacher/',
      payload: {
        summary: { students_count: 28, classrooms_count: 3, at_risk_students: 4, unread_messages: 2 },
        classrooms: [{ id: 1, name: 'SS 2 Gold', grade_level: 'SS2', student_count: 28, is_class_teacher: true }],
        students: [{ id: 99, first_name: 'Femi', last_name: 'Cole', admission_number: 'A-1', classroom: 'SS 2 Gold', attendance_percentage: 93, average_grade: 78.4 }],
        ai_watchlist: [{ student_id: 99, student_name: 'Femi Cole', classroom: 'SS 2 Gold', attendance_risk: 0.2, performance_risk: 0.6, risk_level: 'MEDIUM', flagged_subjects: ['Physics'] }],
        recent_messages: [{ id: 1, counterpart_name: 'Mrs Bello', content: 'Please review Femi this week.', sent_at: '2026-04-10T10:00:00Z', student_name: 'Femi Cole' }],
        subject_assignments: [{ subject_name: 'Physics', subject_code: 'PHY', classroom_name: 'SS 2 Gold', grade_level: 'SS2' }],
      },
      assertions: ['Instruction, interventions, and classroom rhythm', 'Classroom coverage', 'Intervention queue'],
    },
    {
      role: 'parent',
      path: '/app/parent',
      session: {
        user: { id: 4, username: 'parent', first_name: 'Amina', last_name: 'Yusuf', full_name: 'Amina Yusuf', email: 'parent@test.dev' },
        role: 'parent',
        school: { id: 1, name: 'Atlas College' },
        ministry: null,
        permissions: [],
      },
      dashboardPath: '**/api/dashboard/parent/',
      payload: {
        children: [{ id: 11, first_name: 'Sade', last_name: 'Yusuf', admission_number: 'ST-11', classroom: 'JSS 2 Blue', status: 'active' }],
        fees: [{ student_id: 11, student_name: 'Sade Yusuf', total_due: 150000, amount_paid: 100000, balance: 50000, paid: false }],
        attendance: [{ student_id: 11, student_name: 'Sade Yusuf', total_days: 18, present_days: 17, absent_days: 1, late_days: 0, attendance_percentage: 94.4 }],
        ai_insights: [{ student_id: 11, student_name: 'Sade Yusuf', attendance_risk: 0.1, performance_risk: 0.3, flagged_subjects: ['Mathematics'] }],
        messages: { unread_count: 3 },
      },
      assertions: ['A clearer view of your children', 'Children overview', 'Learning attention signal'],
    },
    {
      role: 'bursar',
      path: '/app/bursar',
      session: {
        user: { id: 5, username: 'bursar', first_name: 'Kunle', last_name: 'Ariyo', full_name: 'Kunle Ariyo', email: 'bursar@test.dev' },
        role: 'bursar',
        school: { id: 1, name: 'Atlas College' },
        ministry: null,
        permissions: [],
      },
      dashboardPath: '**/api/dashboard/bursar/',
      payload: {
        school: { id: 1, name: 'Atlas College' },
        financial_summary: { total_due: 1000000, total_paid: 820000, balance: 180000, collection_rate: 82 },
        fees_by_status: [
          { status: 'paid', count: 140, total: 820000 },
          { status: 'partial', count: 18, total: 95000 },
          { status: 'unpaid', count: 12, total: 180000 },
        ],
        total_students: 170,
      },
      assertions: ['Collections command for Atlas College', 'Collection status mix', 'Revenue health'],
    },
  ];

  for (const scenario of roleScenarios) {
    await seedSession(page, scenario.session);
    await page.route('**/api/auth/me/', async (route) => route.fulfill({ json: scenario.session }));
    await page.route(scenario.dashboardPath, async (route) => route.fulfill({ json: scenario.payload }));
    await page.goto(scenario.path);
    for (const text of scenario.assertions) {
      await expect(page.getByText(text).first()).toBeVisible();
    }
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
    await page.unrouteAll({ behavior: 'ignoreErrors' });
  }
});

test('superadmin and ministry dashboards render strategic oversight panels', async ({ page }) => {
  const cases = [
    {
      role: 'superadmin',
      session: {
        user: { id: 8, username: 'superadmin', first_name: 'Zainab', last_name: 'Cole', full_name: 'Zainab Cole', email: 'superadmin@test.dev' },
        role: 'superadmin',
        school: null,
        ministry: null,
        permissions: [],
      },
      route: '**/api/billing/portfolio/',
      payload: {
        currency: 'NGN',
        summary: {
          schools_with_subscriptions: 48,
          active_subscriptions: 41,
          estimated_monthly_run_rate: 24000000,
          renewals_next_30_days: 7,
        },
        tier_mix: [{ tier_name: 'Growth', schools: 18 }],
        watchlist: [{ subscription_id: 1, school_name: 'Atlas College', status: 'past_due', days_until_renewal: 3 }],
        recent_transactions: [{ id: 1, school_name: 'Atlas College', status: 'completed', created_at: '2026-04-10T10:00:00Z' }],
      },
      assertions: ['Portfolio and growth command', 'Tier mix', 'Watchlist'],
    },
    {
      role: 'ministry_admin',
      session: {
        user: { id: 9, username: 'ministry', first_name: 'Bisi', last_name: 'Adeyemi', full_name: 'Bisi Adeyemi', email: 'ministry@test.dev' },
        role: 'ministry_admin',
        school: null,
        ministry: { id: 3, name: 'Oyo State Ministry of Education', currency_code: 'NGN' },
        permissions: [],
      },
      route: '**/api/government/dashboard/ministry/',
      payload: {
        results: [{
          total_schools: 312,
          total_students: 184200,
          collection_rate_percentage: 71.2,
          students_at_risk_count: 1240,
          total_fees_collected: 120000000,
          total_fees_outstanding: 48000000,
          avg_attendance_rate: 87.5,
          overall_pass_rate: 74.3,
          alerts: [{ id: 1, title: 'Attendance drop', message: 'Three districts dropped below threshold.' }],
        }],
      },
      assertions: ['Education system oversight', 'State performance', 'Alerts'],
    },
  ];

  for (const scenario of cases) {
    await seedSession(page, scenario.session);
    await page.route('**/api/auth/me/', async (route) => route.fulfill({ json: scenario.session }));
    await page.route(scenario.route, async (route) => route.fulfill({ json: scenario.payload }));
    await page.goto('/dashboard');
    for (const text of scenario.assertions) {
      await expect(page.getByText(text).first()).toBeVisible();
    }
    await page.context().clearCookies();
    await page.evaluate(() => localStorage.clear());
    await page.unrouteAll({ behavior: 'ignoreErrors' });
  }
});
