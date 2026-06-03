import apiClient from './api-client';

const TOKEN_KEY = 'auth_token';
const SESSION_KEY = 'auth_session';

const splitName = (fullName = '') => {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) {
    return { firstName: '', lastName: '' };
  }

  return {
    firstName: parts[0],
    lastName: parts.slice(1).join(' ') || parts[0],
  };
};

const persistSession = (payload) => {
  if (!payload) return payload;

  if (payload.token) {
    localStorage.setItem(TOKEN_KEY, payload.token);
  }

  const session = {
    user: payload.user || null,
    role: payload.role || null,
    school: payload.school || null,
    ministry: payload.ministry || null,
    permissions: payload.permissions || [],
  };

  localStorage.setItem(SESSION_KEY, JSON.stringify(session));

  if (session.user) {
    localStorage.setItem('user', JSON.stringify(session.user));
  }

  return session;
};

export const getStoredSession = () => {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    console.error('Failed to parse stored session:', error);
    return null;
  }
};

export const getDashboardPathForRole = (role) => {
  const routes = {
    admin: '/dashboard',
    superadmin: '/dashboard',
    ministry_admin: '/dashboard',
    teacher: '/app/teacher',
    student: '/app/student',
    parent: '/app/parent',
    bursar: '/app/bursar',
  };

  return routes[role] || '/dashboard';
};

export const getPlatformOverview = async () => {
  try {
    const response = await apiClient.get('/api/platform/overview/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch platform overview:', error);
    return null;
  }
};

export const getPublicPricing = async () => {
  try {
    const response = await apiClient.get('/api/billing/pricing/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch pricing:', error);
    return null;
  }
};

export const checkSubdomain = async (subdomain, schoolName = '') => {
  try {
    const response = await apiClient.post('/api/platform/check-subdomain/', {
      subdomain,
      school_name: schoolName,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to check subdomain:', error);
    throw error;
  }
};

export const registerSchool = async (data) => {
  const { firstName, lastName } = splitName(data.admin_name);
  const payload = {
    name: data.school_name || data.name,
    subdomain: data.subdomain,
    email: data.school_email || data.email || data.admin_email,
    phone: data.phone || '',
    city: data.city || '',
    state: data.state || '',
    country: data.country || 'Nigeria',
    admin_email: data.admin_email,
    admin_password: data.admin_password,
    admin_first_name: data.admin_first_name || firstName,
    admin_last_name: data.admin_last_name || lastName,
    timezone: data.timezone || 'Africa/Lagos',
    language: data.language || 'en',
    region: data.region || data.country || 'West Africa',
    school_type: data.school_type || 'private',
  };

  try {
    const response = await apiClient.post('/api/platform/register-school/', payload);
    return response.data;
  } catch (error) {
    console.error('Failed to register school:', error);
    throw error;
  }
};

export const loginUser = async (email, password) => {
  try {
    const response = await apiClient.post('/api/auth/login/', {
      email,
      password,
    });
    if (response.data.token) {
      persistSession(response.data);
    }
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

export const logoutUser = async () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(SESSION_KEY);
  localStorage.removeItem('user');
};

export const getCurrentUser = async () => {
  try {
    const response = await apiClient.get('/api/auth/me/');
    const storedToken = localStorage.getItem(TOKEN_KEY);
    persistSession({
      ...response.data,
      token: storedToken,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch current user:', error);
    return null;
  }
};

export const getDashboardData = async (session) => {
  const role = session?.role;

  if (!role) {
    return null;
  }

  if (role === 'admin') {
    const response = await apiClient.get('/api/dashboard/schooladmin/');
    return response.data;
  }

  if (role === 'teacher') {
    const response = await apiClient.get('/api/dashboard/teacher/');
    return response.data;
  }

  if (role === 'student') {
    const response = await apiClient.get('/api/dashboard/student/');
    return response.data;
  }

  if (role === 'parent') {
    const response = await apiClient.get('/api/dashboard/parent/');
    return response.data;
  }

  if (role === 'bursar') {
    const response = await apiClient.get('/api/dashboard/bursar/');
    return response.data;
  }

  if (role === 'superadmin') {
    const response = await apiClient.get('/api/billing/portfolio/');
    return response.data;
  }

  if (role === 'ministry_admin') {
    const response = await apiClient.get('/api/government/dashboard/ministry/');
    return response.data?.results?.[0] || response.data?.[0] || null;
  }

  return null;
};

// ==================== MESSAGING API ====================

export const getMessageContacts = async () => {
  try {
    const response = await apiClient.get('/api/messages/contacts/');
    return response.data || [];
  } catch (error) {
    console.error('Failed to fetch message contacts:', error);
    throw error;
  }
};

export const sendMessage = async (receiverId, content, studentId = null) => {
  try {
    const payload = {
      receiver: receiverId,
      content,
    };
    if (studentId) {
      payload.student = studentId;
    }
    const response = await apiClient.post('/api/messages/', payload);
    return response.data;
  } catch (error) {
    console.error('Failed to send message:', error);
    throw error;
  }
};

export const getInbox = async () => {
  try {
    const response = await apiClient.get('/api/messages/inbox/');
    return response.data || [];
  } catch (error) {
    console.error('Failed to fetch inbox:', error);
    throw error;
  }
};

export const getOutbox = async () => {
  try {
    const response = await apiClient.get('/api/messages/outbox/');
    return response.data || [];
  } catch (error) {
    console.error('Failed to fetch outbox:', error);
    throw error;
  }
};

export const getUnreadCount = async () => {
  try {
    const response = await apiClient.get('/api/messages/unread_count/');
    return response.data?.unread_count || 0;
  } catch (error) {
    console.error('Failed to fetch unread count:', error);
    return 0;
  }
};

export const markMessageAsRead = async (messageId) => {
  try {
    const response = await apiClient.post(`/api/messages/${messageId}/mark_as_read/`);
    return response.data;
  } catch (error) {
    console.error('Failed to mark message as read:', error);
    throw error;
  }
};

export const markAllMessagesAsRead = async () => {
  try {
    const response = await apiClient.post('/api/messages/mark_all_as_read/');
    return response.data;
  } catch (error) {
    console.error('Failed to mark all messages as read:', error);
    throw error;
  }
};

// ==================== EXPORT API ====================

export const exportStudentsData = async (format = 'csv') => {
  try {
    const response = await apiClient.get(`/api/students/export/?format=${format}`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Failed to export students data:', error);
    throw error;
  }
};

export const exportStaffData = async (format = 'csv') => {
  try {
    const response = await apiClient.get(`/api/teachers/export/?format=${format}`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Failed to export staff data:', error);
    throw error;
  }
};

export const exportAttendanceData = async (format = 'csv') => {
  try {
    const response = await apiClient.get(`/api/attendance/export/?format=${format}`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Failed to export attendance data:', error);
    throw error;
  }
};

export const exportFeesData = async (format = 'csv') => {
  try {
    const response = await apiClient.get(`/api/finance/fees/export/?format=${format}`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Failed to export fees data:', error);
    throw error;
  }
};

export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || 'export.csv';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
