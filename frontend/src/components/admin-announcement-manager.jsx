import React, { useState, useEffect } from 'react';
import { Bell, Send, Pin, X, CheckCircle, AlertCircle } from 'lucide-react';
import { LoadingButton } from './quick-wins-animations';

/**
 * AdminAnnouncementManager - World-class announcement system for school admins
 * Restricted to users with role='admin' or 'superadmin'
 */
export const AdminAnnouncementManager = ({ 
  schoolId, 
  userRole, 
  onClose 
}) => {
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [targetRole, setTargetRole] = useState('all');
  const [isPinned, setIsPinned] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [announcements, setAnnouncements] = useState([]);
  const [loadingAnnouncements, setLoadingAnnouncements] = useState(false);

  // Only admins can access this
  if (!['admin', 'superadmin'].includes(userRole)) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
          <Bell className="mx-auto mb-4 h-12 w-12 text-slate-400" />
          <h2 className="text-center font-display text-xl font-bold text-slate-900">Access Denied</h2>
          <p className="mt-2 text-center text-sm text-slate-600">
            Only school administrators can create announcements.
          </p>
          <button
            onClick={onClose}
            className="mt-6 w-full rounded-lg bg-slate-200 px-4 py-2 font-medium text-slate-900 hover:bg-slate-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  const targetOptions = [
    { value: 'all', label: ' All Users', description: 'Students, Teachers, Parents, Admins' },
    { value: 'students', label: ' Students Only', description: 'Visible only to students' },
    { value: 'teachers', label: ' Teachers Only', description: 'Visible only to teachers' },
    { value: 'parents', label: ' Parents Only', description: 'Visible only to parents' },
    { value: 'admin', label: ' Admins Only', description: 'Visible only to administrators' },
  ];

  useEffect(() => {
    fetchAnnouncements();
  }, [schoolId]);

  const fetchAnnouncements = async () => {
    setLoadingAnnouncements(true);
    try {
      const response = await fetch(`/api/platform/announcements/?school=${schoolId}`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setAnnouncements(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch announcements:', err);
    } finally {
      setLoadingAnnouncements(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !message.trim()) {
      setError('Title and message are required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/platform/announcements/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
        },
        body: JSON.stringify({
          title: title.trim(),
          message: message.trim(),
          target_role: targetRole,
          is_pinned: isPinned,
          school: schoolId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create announcement');
      }

      setSuccess(true);
      setTitle('');
      setMessage('');
      setTargetRole('all');
      setIsPinned(false);

      // Refresh announcements
      await fetchAnnouncements();

      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message || 'Failed to send announcement');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (announcementId) => {
    if (!window.confirm('Delete this announcement?')) return;

    try {
      const response = await fetch(`/api/platform/announcements/${announcementId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`,
        },
      });

      if (response.ok) {
        await fetchAnnouncements();
      }
    } catch (err) {
      console.error('Failed to delete announcement:', err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 overflow-y-auto">
      <div className="w-full max-w-2xl rounded-2xl bg-white shadow-2xl">
        {/* Header */}
        <div className="border-b border-slate-200 px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bell className="h-6 w-6 text-brand-600" />
            <h2 className="font-display text-2xl font-bold text-slate-900">Send Announcement</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="max-h-[80vh] overflow-y-auto p-6 space-y-6">
          {/* Success Message */}
          {success && (
            <div className="flex items-center gap-3 rounded-lg border border-green-200 bg-green-50 p-4 animate-pulse">
              <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
              <p className="text-sm text-green-800">Announcement sent successfully!</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-4">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Title */}
            <div>
              <label className="mb-2 block font-medium text-slate-900">Announcement Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Important Update on Academic Calendar"
                maxLength={255}
                className="w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20"
              />
              <p className="mt-1 text-xs text-slate-500">{title.length}/255 characters</p>
            </div>

            {/* Message */}
            <div>
              <label className="mb-2 block font-medium text-slate-900">Message</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter your announcement message..."
                rows={5}
                className="w-full rounded-lg border border-slate-300 px-4 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-600/20"
              />
            </div>

            {/* Target Role */}
            <div>
              <label className="mb-3 block font-medium text-slate-900">Send to</label>
              <div className="grid gap-2 sm:grid-cols-2">
                {targetOptions.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setTargetRole(option.value)}
                    className={`rounded-lg border-2 p-3 text-left transition-all ${
                      targetRole === option.value
                        ? 'border-brand-600 bg-brand-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <p className="font-medium text-slate-900">{option.label}</p>
                    <p className="text-xs text-slate-600">{option.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Pin Option */}
            <div className="flex items-center gap-3 rounded-lg bg-slate-50 p-4">
              <input
                type="checkbox"
                id="pin-announcement"
                checked={isPinned}
                onChange={(e) => setIsPinned(e.target.checked)}
                className="h-5 w-5 rounded border-slate-300 text-brand-600"
              />
              <label htmlFor="pin-announcement" className="flex items-center gap-2 text-sm text-slate-700">
                <Pin className="h-4 w-4" />
                Pin to top of feed for important announcements
              </label>
            </div>

            {/* Submit */}
            <LoadingButton
              type="submit"
              loading={loading}
              disabled={!title.trim() || !message.trim()}
              className="w-full gap-2 rounded-lg bg-gradient-to-r from-brand-600 to-brand-700 px-4 py-3 text-white hover:from-brand-700 hover:to-brand-800 disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
              Send Announcement
            </LoadingButton>
          </form>

          {/* Recent Announcements */}
          <div className="border-t border-slate-200 pt-6">
            <h3 className="font-medium text-slate-900 mb-4">Recent Announcements</h3>
            {loadingAnnouncements ? (
              <div className="space-y-2">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="h-16 animate-pulse rounded-lg bg-slate-200" />
                ))}
              </div>
            ) : announcements.length === 0 ? (
              <p className="text-sm text-slate-600">No announcements yet</p>
            ) : (
              <div className="space-y-2">
                {announcements.slice(0, 5).map((announcement) => (
                  <div
                    key={announcement.id}
                    className={`rounded-lg border p-3 flex items-start justify-between ${
                      announcement.is_pinned
                        ? 'border-amber-200 bg-amber-50'
                        : 'border-slate-200 bg-slate-50'
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        {announcement.is_pinned && <Pin className="h-4 w-4 text-amber-600 flex-shrink-0" />}
                        <p className="font-medium text-slate-900 truncate">{announcement.title}</p>
                      </div>
                      <p className="text-xs text-slate-600 mt-1">To: {announcement.target_role || 'all'}</p>
                    </div>
                    <button
                      onClick={() => handleDelete(announcement.id)}
                      className="ml-2 text-slate-400 hover:text-red-600 transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
