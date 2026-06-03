import React, { useState, useEffect } from 'react';
import { Bell, X, Send, Users, BookOpen, Users2, User, Lock } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/form';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';

/**
 * AnnouncementPanel - World-class announcement UI for school admins
 * 
 * Features:
 * - Create announcements with role-based targeting
 * - Pin important announcements
 * - Real-time message delivery via WebSocket
 * - Beautiful card-based layout with Playfair Display headings
 * - Smooth animations and transitions
 */
export const AnnouncementPanel = ({ 
  onClose, 
  onSubmit, 
  isAdmin = false,
  announcements = [],
  isLoading = false 
}) => {
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [targetRole, setTargetRole] = useState('all');
  const [isPinned, setIsPinned] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const roleOptions = [
    { value: 'all', label: 'All Users', icon: Users, color: 'bg-blue-100 text-blue-700' },
    { value: 'students', label: 'Students Only', icon: BookOpen, color: 'bg-purple-100 text-purple-700' },
    { value: 'teachers', label: 'Teachers Only', icon: Users2, color: 'bg-green-100 text-green-700' },
    { value: 'parents', label: 'Parents Only', icon: User, color: 'bg-orange-100 text-orange-700' },
    { value: 'admin', label: 'Admins Only', icon: Lock, color: 'bg-red-100 text-red-700' },
  ];

  const selectedRoleOption = roleOptions.find(r => r.value === targetRole);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !message.trim()) return;
    
    setSubmitting(true);
    try {
      await onSubmit({
        title,
        message,
        target_role: targetRole,
        is_pinned: isPinned,
      });
      setTitle('');
      setMessage('');
      setTargetRole('all');
      setIsPinned(false);
      setShowForm(false);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-lg w-full">
      {/* Floating Button */}
      {!showForm && (
        <button
          onClick={() => setShowForm(true)}
          className="w-full mb-4 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-brand-600 text-white rounded-full shadow-lg hover:shadow-xl hover:from-blue-700 hover:to-brand-700 transition-all duration-200 transform hover:scale-105"
        >
          <Bell className="w-5 h-5" />
          <span className="font-medium">Send Announcement</span>
        </button>
      )}

      {/* Announcement Form Panel */}
      {showForm && (
        <Card className="shadow-2xl border-0">
          <CardContent className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-display font-bold text-slate-900">
                Broadcast Announcement
              </h2>
              <button
                onClick={() => setShowForm(false)}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-slate-900 mb-2">
                  Announcement Title
                </label>
                <Input
                  type="text"
                  placeholder="e.g., School Holiday Notice"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="text-base"
                  required
                />
              </div>

              {/* Message */}
              <div>
                <label className="block text-sm font-medium text-slate-900 mb-2">
                  Message
                </label>
                <textarea
                  placeholder="Write your announcement message here..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20 focus:outline-none resize-none text-base"
                  required
                />
              </div>

              {/* Target Role Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-900 mb-3">
                  Send to
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {roleOptions.map((option) => {
                    const Icon = option.icon;
                    const isSelected = targetRole === option.value;
                    return (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => setTargetRole(option.value)}
                        className={`
                          p-3 rounded-lg border-2 transition-all duration-200
                          flex items-center gap-2 font-medium text-sm
                          ${isSelected
                            ? 'border-brand-600 bg-brand-50'
                            : 'border-slate-200 bg-white hover:border-slate-300'
                          }
                        `}
                      >
                        <Icon className="w-4 h-4" />
                        {option.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Pin Option */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isPinned}
                  onChange={(e) => setIsPinned(e.target.checked)}
                  className="w-4 h-4 text-brand-600 rounded focus:ring-2 focus:ring-brand-600"
                />
                <span className="text-sm font-medium text-slate-700">
                   Pin this announcement to top
                </span>
              </label>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={submitting || !title.trim() || !message.trim()}
                className="w-full py-3 bg-gradient-to-r from-blue-600 to-brand-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
              >
                {submitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Send Announcement
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Recent Announcements Feed */}
      {!showForm && announcements.length > 0 && (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {announcements.map((announcement) => {
            const roleOption = roleOptions.find(r => r.value === announcement.target_role);
            const RoleIcon = roleOption?.icon;
            
            return (
              <Card key={announcement.id} className={`border-l-4 ${
                announcement.is_pinned 
                  ? 'border-l-yellow-500 bg-yellow-50' 
                  : 'border-l-brand-600 bg-white'
              }`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-display font-bold text-slate-900">
                          {announcement.title}
                        </h3>
                        {announcement.is_pinned && (
                          <span className="text-lg"></span>
                        )}
                      </div>
                      <p className="text-sm text-slate-600 mb-2">
                        {announcement.message}
                      </p>
                      <div className="flex items-center gap-2 flex-wrap">
                        {RoleIcon && (
                          <Badge className={roleOption?.color}>
                            <RoleIcon className="w-3 h-3 mr-1" />
                            {roleOption?.label}
                          </Badge>
                        )}
                        <span className="text-xs text-slate-500">
                          {new Date(announcement.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AnnouncementPanel;
