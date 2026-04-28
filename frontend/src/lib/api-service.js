import apiClient from './api-client';
import { withRetry, withTimeout, requestDeduplicator, generateCacheKey } from './network-resilience';
import { handleAPIError } from './api-errors';
import { log } from './config';

// ============ USER MANAGEMENT APIs ============

/**
 * Get list of users by role
 * @param {string} role - 'student' or 'teacher'
 * @param {object} params - Query parameters (search, filter, page, etc.)
 * @returns {Promise<Array>}
 */
export const getUsers = async (role, params = {}) => {
  const cacheKey = generateCacheKey('GET', `/api/users/`, { params: { role, ...params } });
  
  return requestDeduplicator.execute(cacheKey, () =>
    withRetry(async () => {
      try {
        const response = await withTimeout(
          apiClient.get(`/api/users/`, { params: { role, ...params } })
        );
        return response.data.results || response.data;
      } catch (error) {
        const apiError = handleAPIError(error);
        log.error(`Failed to fetch ${role}s:`, apiError);
        throw apiError;
      }
    })
  );
};

/**
 * Get single user by ID
 * @param {number} userId
 * @returns {Promise<Object>}
 */
export const getUser = async (userId) => {
  const cacheKey = generateCacheKey('GET', `/api/users/${userId}/`);
  
  return requestDeduplicator.execute(cacheKey, () =>
    withRetry(async () => {
      try {
        const response = await withTimeout(
          apiClient.get(`/api/users/${userId}/`)
        );
        return response.data;
      } catch (error) {
        const apiError = handleAPIError(error);
        log.error(`Failed to fetch user ${userId}:`, apiError);
        throw apiError;
      }
    })
  );
};

/**
 * Create new user (student or teacher)
 * @param {object} userData
 * @returns {Promise<Object>}
 */
export const createUser = async (userData) => {
  // Don't cache/deduplicate POST requests
  return withRetry(async () => {
    try {
      const response = await withTimeout(
        apiClient.post('/api/users/', userData)
      );
      return response.data;
    } catch (error) {
      const apiError = handleAPIError(error);
      log.error('Failed to create user:', apiError);
      throw apiError;
    }
  });
};

/**
 * Update existing user
 * @param {number} userId
 * @param {object} userData
 * @returns {Promise<Object>}
 */
export const updateUser = async (userId, userData) => {
  // Clear related cache on update
  requestDeduplicator.clear(generateCacheKey('GET', `/api/users/${userId}/`));
  
  return withRetry(async () => {
    try {
      const response = await withTimeout(
        apiClient.patch(`/api/users/${userId}/`, userData)
      );
      return response.data;
    } catch (error) {
      const apiError = handleAPIError(error);
      log.error(`Failed to update user ${userId}:`, apiError);
      throw apiError;
    }
  });
};

/**
 * Delete user
 * @param {number} userId
 * @returns {Promise<void>}
 */
export const deleteUser = async (userId) => {
  // Clear cache on delete
  requestDeduplicator.clear(generateCacheKey('GET', `/api/users/${userId}/`));
  
  return withRetry(async () => {
    try {
      await withTimeout(
        apiClient.delete(`/api/users/${userId}/`)
      );
    } catch (error) {
      const apiError = handleAPIError(error);
      log.error(`Failed to delete user ${userId}:`, apiError);
      throw apiError;
    }
  });
};

/**
 * Bulk import users from CSV
 * @param {File} csvFile
 * @param {string} role - 'student' or 'teacher'
 * @returns {Promise<Object>} - Import result with counts
 */
export const bulkImportUsers = async (csvFile, role) => {
  return withRetry(async () => {
    try {
      const formData = new FormData();
      formData.append('file', csvFile);
      formData.append('role', role);

      const response = await withTimeout(
        apiClient.post('/api/bulk-import/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
      );
      return response.data;
    } catch (error) {
      const apiError = handleAPIError(error);
      log.error('Failed to bulk import users:', apiError);
      throw apiError;
    }
  });
};

// ============ ADMIN SETTINGS APIs ============

/**
 * Get school branding settings
 * @returns {Promise<Object>}
 */
export const getBrandingSettings = async () => {
  const cacheKey = generateCacheKey('GET', '/api/platform/branding-admin/');
  
  return requestDeduplicator.execute(cacheKey, () =>
    withRetry(async () => {
      try {
        const response = await withTimeout(
          apiClient.get('/api/platform/branding-admin/')
        );
        return response.data;
      } catch (error) {
        const apiError = handleAPIError(error);
        log.error('Failed to fetch branding settings:', apiError);
        throw apiError;
      }
    })
  );
};

/**
 * Update school branding
 * @param {object} brandingData - { name, email, logo_url, primary_color, secondary_color }
 * @returns {Promise<Object>}
 */
export const updateBrandingSettings = async (brandingData) => {
  // Clear cache on update
  requestDeduplicator.clear(generateCacheKey('GET', '/api/platform/branding-admin/'));
  
  return withRetry(async () => {
    try {
      const response = await withTimeout(
        apiClient.patch('/api/platform/branding-admin/', brandingData)
      );
      return response.data;
    } catch (error) {
      const apiError = handleAPIError(error);
      log.error('Failed to update branding settings:', apiError);
      throw apiError;
    }
  });
};

/**
 * Get school permission settings
 * @returns {Promise<Object>}
 */
export const getPermissionSettings = async () => {
  const cacheKey = generateCacheKey('GET', '/api/government/permissions/roles/', {
    params: { role: 'school_admin' },
  });
  
  return requestDeduplicator.execute(cacheKey, () =>
    withRetry(async () => {
      try {
        const response = await withTimeout(
          apiClient.get('/api/government/permissions/roles/', { params: { role: 'school_admin' } })
        );
        return response.data.results || response.data;
      } catch (error) {
        const apiError = handleAPIError(error);
        log.error('Failed to fetch permission settings:', apiError);
        throw apiError;
      }
    })
  );
};

/**
 * Update school permissions
 * @param {object} permissionsData
 * @returns {Promise<Object>}
 */
export const updatePermissionSettings = async (permissionsData) => {
  // Clear cache on update
  requestDeduplicator.clear(generateCacheKey('GET', '/api/government/permissions/roles/', {
    params: { role: 'school_admin' },
  }));
  
  return withRetry(async () => {
    try {
      const targetId = permissionsData?.id;
      if (!targetId) {
        throw new Error('Permission group id is required for updates');
      }
      const response = await withTimeout(apiClient.patch(`/api/government/permissions/roles/${targetId}/`, permissionsData));
      return response.data;
    } catch (error) {
      const apiError = handleAPIError(error);
      log.error('Failed to update permission settings:', apiError);
      throw apiError;
    }
  });
};

/**
 * Get notification settings
 * @returns {Promise<Object>}
 */
export const getNotificationSettings = async () => {
  const cacheKey = generateCacheKey('GET', '/api/school-settings/current/');
  
  return requestDeduplicator.execute(cacheKey, () =>
    withRetry(async () => {
      try {
        const response = await withTimeout(
          apiClient.get('/api/school-settings/current/')
        );
        return {
          email: response.data.enable_email_alerts,
          sms: response.data.enable_sms_alerts,
          daily_digest: response.data.enable_teacher_portal,
          notification_email: response.data.notification_email,
        };
      } catch (error) {
        const apiError = handleAPIError(error);
        log.error('Failed to fetch notification settings:', apiError);
        throw apiError;
      }
    })
  );
};

/**
 * Update notification settings
 * @param {object} notificationsData - { email, sms, daily_digest }
 * @returns {Promise<Object>}
 */
export const updateNotificationSettings = async (notificationsData) => {
  // Clear cache on update
  requestDeduplicator.clear(generateCacheKey('GET', '/api/school-settings/current/'));
  
  return withRetry(async () => {
    try {
      const response = await withTimeout(
        apiClient.patch('/api/school-settings/current/', {
          enable_email_alerts: notificationsData.email,
          enable_sms_alerts: notificationsData.sms,
          enable_teacher_portal: notificationsData.daily_digest,
          notification_email: notificationsData.notification_email,
        })
      );
      return response.data;
    } catch (error) {
      const apiError = handleAPIError(error);
      log.error('Failed to update notification settings:', apiError);
      throw apiError;
    }
  });
};

/**
 * Get audit logs
 * @param {object} params - Query parameters (page, limit, filter, etc.)
 * @returns {Promise<Object>}
 */
export const getAuditLogs = async (params = {}) => {
  const cacheKey = generateCacheKey('GET', '/api/government/audit-logs/', { params });
  
  return requestDeduplicator.execute(cacheKey, () =>
    withRetry(async () => {
      try {
        const response = await withTimeout(
          apiClient.get('/api/government/audit-logs/', { params })
        );
        return response.data.results || response.data;
      } catch (error) {
        const apiError = handleAPIError(error);
        log.error('Failed to fetch audit logs:', apiError);
        throw apiError;
      }
    })
  );
};

/**
 * Export audit logs as CSV
 * @param {object} params - Query parameters for filtering
 * @returns {Promise<Blob>}
 */
export const exportAuditLogs = async (params = {}) => {
  return withRetry(async () => {
    try {
      const response = await withTimeout(
        apiClient.get('/api/government/audit-logs/export/', {
          params,
          responseType: 'blob',
        })
      );
      return response.data;
    } catch (error) {
      const apiError = handleAPIError(error);
      log.error('Failed to export audit logs:', apiError);
      throw apiError;
    }
  });
};

// ============ DASHBOARD APIs ============

/**
 * Get dashboard data based on user role
 * Replaces the generic getDashboardData from django.js with specific endpoints
 */
export const getDashboardByRole = {
  student: async () => {
    const cacheKey = generateCacheKey('GET', '/api/dashboard/student/');
    return requestDeduplicator.execute(cacheKey, () =>
      withRetry(async () => {
        try {
          const response = await withTimeout(
            apiClient.get('/api/dashboard/student/')
          );
          return response.data;
        } catch (error) {
          const apiError = handleAPIError(error);
          log.error('Failed to fetch student dashboard:', apiError);
          throw apiError;
        }
      })
    );
  },

  teacher: async () => {
    const cacheKey = generateCacheKey('GET', '/api/dashboard/teacher/');
    return requestDeduplicator.execute(cacheKey, () =>
      withRetry(async () => {
        try {
          const response = await withTimeout(
            apiClient.get('/api/dashboard/teacher/')
          );
          return response.data;
        } catch (error) {
          const apiError = handleAPIError(error);
          log.error('Failed to fetch teacher dashboard:', apiError);
          throw apiError;
        }
      })
    );
  },

  parent: async () => {
    const cacheKey = generateCacheKey('GET', '/api/dashboard/parent/');
    return requestDeduplicator.execute(cacheKey, () =>
      withRetry(async () => {
        try {
          const response = await withTimeout(
            apiClient.get('/api/dashboard/parent/')
          );
          return response.data;
        } catch (error) {
          const apiError = handleAPIError(error);
          log.error('Failed to fetch parent dashboard:', apiError);
          throw apiError;
        }
      })
    );
  },

  bursar: async () => {
    const cacheKey = generateCacheKey('GET', '/api/dashboard/bursar/');
    return requestDeduplicator.execute(cacheKey, () =>
      withRetry(async () => {
        try {
          const response = await withTimeout(
            apiClient.get('/api/dashboard/bursar/')
          );
          return response.data;
        } catch (error) {
          const apiError = handleAPIError(error);
          log.error('Failed to fetch bursar dashboard:', apiError);
          throw apiError;
        }
      })
    );
  },

  admin: async () => {
    const cacheKey = generateCacheKey('GET', '/api/dashboard/schooladmin/');
    return requestDeduplicator.execute(cacheKey, () =>
      withRetry(async () => {
        try {
          const response = await withTimeout(
            apiClient.get('/api/dashboard/schooladmin/')
          );
          return response.data;
        } catch (error) {
          const apiError = handleAPIError(error);
          log.error('Failed to fetch admin dashboard:', apiError);
          throw apiError;
        }
      })
    );
  },
};
