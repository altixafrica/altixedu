import React from 'react';
import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';

import { DashboardPage } from './pages/dashboard';
import { StudentDashboardPage } from './pages/student-dashboard';
import { TeacherDashboardPage } from './pages/teacher-dashboard';
import { ParentDashboardPage } from './pages/parent-dashboard';
import { BursarDashboardPage } from './pages/bursar-dashboard';
import { AdminSettingsPage } from './pages/admin-settings';
import { UserManagementPage } from './pages/user-management';
import { AnalyticsDashboardPage } from './pages/analytics-dashboard';
import { GetStartedPage } from './pages/get-started';
import { HomePage } from './pages/home';
import { LoginPage } from './pages/login';
import { NotFoundPage } from './pages/not-found';
import { ParentsPage } from './pages/parents';
import { PricingPage } from './pages/pricing';
import { SchoolAdminsPage } from './pages/school-admins';
import { TeachersPage } from './pages/teachers';
import { MessagingDemoPage } from './pages/messaging-demo';
import { ToastProvider } from './lib/toast-context';
import { ThemeProvider } from './lib/theme-context';
import { Toast } from './components/toast';
import { ErrorBoundary } from './components/error-boundary';
import { ErrorProvider, ErrorBoundary as ErrorUIBoundary } from './components/error-display';
import { OnboardingProvider } from './components/onboarding';
import { DashboardPanelProvider } from './components/dashboard-panel-context';
import { SkipToContentLink } from './components/skip-to-content';
import { useServiceWorker } from './hooks/use-service-worker';

function App() {
  // Register service worker for offline capability
  useServiceWorker();
  return (
    <ErrorBoundary>
      <ErrorProvider>
        <OnboardingProvider>
          <DashboardPanelProvider>
            <ThemeProvider>
              <ToastProvider>
                <Router>
              <SkipToContentLink mainContentId="main-content" />
              <main id="main-content">
            <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/get-started" element={<GetStartedPage />} />
        <Route path="/school-admins" element={<SchoolAdminsPage />} />
        <Route path="/teachers" element={<TeachersPage />} />
        <Route path="/parents" element={<ParentsPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/messaging-demo" element={<MessagingDemoPage />} />
        
        {/* Dashboard routes - role-based */}
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/app/dashboard" element={<Navigate replace to="/dashboard" />} />
        <Route path="/app/student" element={<StudentDashboardPage />} />
        <Route path="/app/student/dashboard" element={<Navigate replace to="/app/student" />} />
        <Route path="/app/teacher" element={<TeacherDashboardPage />} />
        <Route path="/app/teacher/dashboard" element={<Navigate replace to="/app/teacher" />} />
        <Route path="/app/parent" element={<ParentDashboardPage />} />
        <Route path="/app/parent/dashboard" element={<Navigate replace to="/app/parent" />} />
        <Route path="/app/bursar" element={<BursarDashboardPage />} />
        <Route path="/app/bursar/dashboard" element={<Navigate replace to="/app/bursar" />} />
        <Route path="/app/admin/settings" element={<AdminSettingsPage />} />
        <Route path="/app/admin/users" element={<UserManagementPage />} />
        <Route path="/app/admin/analytics" element={<AnalyticsDashboardPage />} />
        <Route path="/app/analytics" element={<AnalyticsDashboardPage />} />
        <Route path="/settings" element={<AdminSettingsPage />} />
        <Route path="/users" element={<UserManagementPage />} />
        
        {/* Fallback */}
        <Route path="*" element={<NotFoundPage />} />
            </Routes>
            <Toast />
          </main>
        </Router>
      </ToastProvider>
    </ThemeProvider>
    </DashboardPanelProvider>
    </OnboardingProvider>
    </ErrorProvider>
    </ErrorBoundary>
  );
}

export default App;
