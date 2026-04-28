import React from 'react';
import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';

import { DashboardPage } from './pages/dashboard';
import { StudentDashboardPage } from './pages/student-dashboard';
import { TeacherDashboardPage } from './pages/teacher-dashboard';
import { ParentDashboardPage } from './pages/parent-dashboard';
import { BursarDashboardPage } from './pages/bursar-dashboard';
import { AdminSettingsPage } from './pages/admin-settings';
import { UserManagementPage } from './pages/user-management';
import { GetStartedPage } from './pages/get-started';
import { HomePage } from './pages/home';
import { LoginPage } from './pages/login';
import { NotFoundPage } from './pages/not-found';
import { ParentsPage } from './pages/parents';
import { PricingPage } from './pages/pricing';
import { SchoolAdminsPage } from './pages/school-admins';
import { TeachersPage } from './pages/teachers';
import { ToastProvider } from './lib/toast-context';
import { Toast } from './components/toast';
import { ErrorBoundary } from './components/error-boundary';

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/get-started" element={<GetStartedPage />} />
        <Route path="/school-admins" element={<SchoolAdminsPage />} />
        <Route path="/teachers" element={<TeachersPage />} />
        <Route path="/parents" element={<ParentsPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        
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
        <Route path="/settings" element={<AdminSettingsPage />} />
        <Route path="/users" element={<UserManagementPage />} />
        
        {/* Fallback */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <Toast />
        </Router>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
