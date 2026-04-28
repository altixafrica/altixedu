import { expect, test } from '@playwright/test';

const seedSession = async (page, session) => {
  await page.addInitScript((payload) => {
    localStorage.setItem('auth_token', 'test-token');
    localStorage.setItem('user', JSON.stringify(payload.user));
    localStorage.setItem('auth_session', JSON.stringify(payload));
  }, session);
};

test('student workspace renders key learning panels', async ({ page }) => {
  const session = {
    user: {
      id: 41,
      username: 'student01',
      first_name: 'Ada',
      last_name: 'Okafor',
      full_name: 'Ada Okafor',
      email: 'ada@student.altixedu.test',
    },
    role: 'student',
    school: {
      id: 7,
      name: 'Lagos Future Academy',
    },
    ministry: null,
    permissions: [],
  };

  await seedSession(page, session);

  await page.route('**/api/auth/me/', async (route) => {
    await route.fulfill({ json: session });
  });

  await page.route('**/api/dashboard/student/', async (route) => {
    await route.fulfill({
      json: {
        user: {
          id: 41,
          name: 'Ada Okafor',
          email: 'ada@student.altixedu.test',
          role: 'student',
          school: 'Lagos Future Academy',
        },
        student: {
          id: 301,
          first_name: 'Ada',
          last_name: 'Okafor',
          admission_number: 'LFA-2031',
          classroom: 'JSS 3 Gold',
          status: 'active',
          gender: 'female',
        },
        summary: {
          attendance_percentage: 94.4,
          present_days: 17,
          absent_days: 1,
          late_days: 0,
          average_grade: 81.6,
          subjects_count: 4,
          unread_messages: 2,
        },
        subjects: [
          { id: 1, name: 'Mathematics', code: 'MTH' },
          { id: 2, name: 'English Language', code: 'ENG' },
          { id: 3, name: 'Basic Science', code: 'SCI' },
          { id: 4, name: 'Civic Education', code: 'CIV' },
        ],
        results: [
          { id: 10, subject_name: 'Mathematics', exam_name: 'Midterm', score: 84, recorded_at: '2026-04-10T08:00:00Z' },
          { id: 11, subject_name: 'English Language', exam_name: 'Midterm', score: 79, recorded_at: '2026-04-09T08:00:00Z' },
        ],
        attendance: [
          { id: 1, date: '2026-04-18', status: 'present' },
          { id: 2, date: '2026-04-17', status: 'present' },
        ],
        ai_insight: {
          attendance_risk: 0.1,
          performance_risk: 0.22,
          overall_risk: 0.19,
          risk_level: 'LOW',
          flagged_subjects: ['English Language'],
          recommendations: ['Review comprehension passages twice weekly.'],
        },
        settings: {},
      },
    });
  });

  await page.goto('/app/student');

  await expect(page.getByRole('heading', { name: /Progress overview for Ada/i })).toBeVisible();
  await expect(page.getByText('Academic snapshot')).toBeVisible();
  await expect(page.getByText('Recent results')).toBeVisible();
  await expect(page.getByText('Attendance trend')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Performance signal' })).toBeVisible();
  await expect(page.getByText('English Language').first()).toBeVisible();
});

test('admin settings and user management render with mocked school operations data', async ({ page }) => {
  const session = {
    user: {
      id: 2,
      username: 'principal',
      first_name: 'Tunde',
      last_name: 'Adebayo',
      full_name: 'Tunde Adebayo',
      email: 'principal@altixedu.test',
    },
    role: 'admin',
    school: {
      id: 15,
      name: 'Cedar Heights College',
    },
    ministry: null,
    permissions: [],
  };

  await seedSession(page, session);

  await page.route('**/api/auth/me/', async (route) => {
    await route.fulfill({ json: session });
  });

  await page.route('**/api/platform/branding-admin/', async (route) => {
    if (route.request().method() === 'PATCH') {
      await route.fulfill({ json: { success: true } });
      return;
    }
    await route.fulfill({
      json: {
        name: 'Cedar Heights College',
        email: 'hello@cedarheights.edu',
        primary_color: '#0f172a',
        secondary_color: '#1d4ed8',
        logo_url: '',
      },
    });
  });

  await page.route('**/api/school-settings/current/', async (route) => {
    if (route.request().method() === 'PATCH') {
      await route.fulfill({ json: { success: true } });
      return;
    }
    await route.fulfill({
      json: {
        enable_email_alerts: true,
        enable_sms_alerts: false,
        enable_teacher_portal: true,
        notification_email: 'hello@cedarheights.edu',
      },
    });
  });

  await page.route('**/api/users/**', async (route) => {
    await route.fulfill({
      json: [
        {
          id: 7,
          first_name: 'Ifeoma',
          last_name: 'Eze',
          email: 'ifeoma@student.test',
          username: 'ifeoma.eze',
          role: 'student',
          classroom: 'SS 2 Blue',
          phone: '',
          status: 'active',
        },
        {
          id: 8,
          first_name: 'David',
          last_name: 'Aina',
          email: 'david@student.test',
          username: 'david.aina',
          role: 'student',
          classroom: 'SS 1 Gold',
          phone: '',
          status: 'active',
        },
      ],
    });
  });

  await page.goto('/app/admin/settings');
  await expect(page.getByRole('heading', { name: /Brand, permissions, and operating preferences/i })).toBeVisible();
  await expect(page.getByText('Brand preview')).toBeVisible();
  await expect(page.locator('#school-name')).toHaveValue('Cedar Heights College');

  await page.goto('/app/admin/users');
  await expect(page.getByRole('heading', { name: /People, identity, and onboarding flow/i })).toBeVisible();
  await expect(page.getByText('Students directory')).toBeVisible();
  await expect(page.getByText('Ifeoma Eze')).toBeVisible();
  await expect(page.getByText('David Aina')).toBeVisible();
});
