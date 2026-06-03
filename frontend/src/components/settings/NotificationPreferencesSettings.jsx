import React, { useState, useEffect } from 'react';
import axiosInstance from '../api/axiosInstance';

const NotificationPreferencesSettings = () => {
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [saving, setSaving] = useState(false);

  // Fetch current preferences
  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/notification-preferences/my_preferences/');
      setPreferences(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load preferences');
      console.error('Error fetching preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (field) => {
    setPreferences(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await axiosInstance.patch('/notification-preferences/my_preferences/', preferences);
      setPreferences(response.data);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save preferences');
      console.error('Error saving preferences:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleEnableAll = async () => {
    try {
      setSaving(true);
      const response = await axiosInstance.post('/notification-preferences/enable_all/');
      setPreferences(response.data);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to enable all notifications');
      console.error('Error enabling notifications:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDisableAll = async () => {
    try {
      setSaving(true);
      const response = await axiosInstance.post('/notification-preferences/disable_all/');
      setPreferences(response.data);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to disable all notifications');
      console.error('Error disabling notifications:', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-gray-600">Loading preferences...</span>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-700 font-semibold">Unable to load notification preferences</p>
        <button 
          onClick={fetchPreferences}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Notification Preferences</h1>
        <p className="text-gray-600">Manage how and when you receive notifications</p>
      </div>

      {/* Alert Messages */}
      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          Preferences saved successfully!
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          {error}
        </div>
      )}

      {/* Quick Actions */}
      <div className="mb-8 flex gap-3">
        <button 
          onClick={handleEnableAll}
          disabled={saving}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
        >
          Enable All
        </button>
        <button 
          onClick={handleDisableAll}
          disabled={saving}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50"
        >
          Disable All
        </button>
      </div>

      {/* Notification Channels */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Notification Channels</h2>
        <div className="space-y-4">
          {/* Email */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900">Email</h3>
              <p className="text-sm text-gray-600">Receive notifications via email</p>
            </div>
            <input 
              type="checkbox" 
              checked={preferences.email_enabled || false}
              onChange={() => handleToggle('email_enabled')}
              className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* In-App */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900">In-App</h3>
              <p className="text-sm text-gray-600">Show notifications in the app</p>
            </div>
            <input 
              type="checkbox" 
              checked={preferences.in_app_enabled || false}
              onChange={() => handleToggle('in_app_enabled')}
              className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Notification Types */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Notification Types</h2>
        <div className="space-y-4">
          {/* Announcements */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900"> Announcements</h3>
              <p className="text-sm text-gray-600">School updates and announcements</p>
            </div>
            <input 
              type="checkbox" 
              checked={preferences.announcements_enabled || false}
              onChange={() => handleToggle('announcements_enabled')}
              className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Messages */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900"> Messages</h3>
              <p className="text-sm text-gray-600">Direct messages from teachers and staff</p>
            </div>
            <input 
              type="checkbox" 
              checked={preferences.messages_enabled || false}
              onChange={() => handleToggle('messages_enabled')}
              className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Grades */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900"> Grades</h3>
              <p className="text-sm text-gray-600">New exam results and grades posted</p>
            </div>
            <input 
              type="checkbox" 
              checked={preferences.grades_enabled || false}
              onChange={() => handleToggle('grades_enabled')}
              className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Attendance */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900"> Attendance</h3>
              <p className="text-sm text-gray-600">Attendance alerts and warnings</p>
            </div>
            <input 
              type="checkbox" 
              checked={preferences.attendance_enabled || false}
              onChange={() => handleToggle('attendance_enabled')}
              className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Fees */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900"> Fees</h3>
              <p className="text-sm text-gray-600">Fee payment reminders</p>
            </div>
            <input 
              type="checkbox" 
              checked={preferences.fees_enabled || false}
              onChange={() => handleToggle('fees_enabled')}
              className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Schedule */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900"> Schedule</h3>
              <p className="text-sm text-gray-600">Timetable changes and updates</p>
            </div>
            <input 
              type="checkbox" 
              checked={preferences.schedule_enabled || false}
              onChange={() => handleToggle('schedule_enabled')}
              className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* System */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900"> System</h3>
              <p className="text-sm text-gray-600">Important system notifications and maintenance</p>
            </div>
            <input 
              type="checkbox" 
              checked={preferences.system_enabled || false}
              onChange={() => handleToggle('system_enabled')}
              className="w-6 h-6 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end gap-3">
        <button 
          onClick={fetchPreferences}
          disabled={saving}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 disabled:opacity-50"
        >
          Cancel
        </button>
        <button 
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center"
        >
          {saving ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Saving...
            </>
          ) : (
            'Save Preferences'
          )}
        </button>
      </div>
    </div>
  );
};

export default NotificationPreferencesSettings;
