import React, { useState, useEffect } from 'react';
import { Send, MessageSquare, X, Loader } from 'lucide-react';
import {
  sendMessage,
  getInbox,
  getMessageContacts,
  markMessageAsRead,
  getUnreadCount,
} from '../lib/django';
import { useError } from './error-display';
import { formatErrorForDisplay } from '../lib/error-handler';

export const MessagingPanel = ({ isOpen, onClose, currentUser }) => {
  const [activeTab, setActiveTab] = useState('inbox');
  const [messages, setMessages] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);
  const [messageContent, setMessageContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const { addError } = useError();

  // Load messages on mount and when tab changes
  useEffect(() => {
    if (isOpen) {
      loadMessages();
      loadContacts();
      loadUnreadCount();
    }
  }, [isOpen, activeTab]);

  const loadMessages = async () => {
    setLoading(true);
    try {
      const data = await getInbox();
      setMessages(data);
    } catch (error) {
      const formatted = formatErrorForDisplay(error);
      addError(formatted.message);
    } finally {
      setLoading(false);
    }
  };

  const loadContacts = async () => {
    try {
      const data = await getMessageContacts();
      setContacts(data);
    } catch (error) {
      console.error('Failed to load contacts:', error);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const count = await getUnreadCount();
      setUnreadCount(count);
    } catch (error) {
      console.error('Failed to load unread count:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!selectedContact || !messageContent.trim()) return;

    setLoading(true);
    try {
      await sendMessage(selectedContact.id, messageContent.trim());
      setMessageContent('');
      setSelectedContact(null);
      await loadMessages();
      await loadUnreadCount();
    } catch (error) {
      const formatted = formatErrorForDisplay(error);
      addError(formatted.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (messageId) => {
    try {
      await markMessageAsRead(messageId);
      await loadMessages();
      await loadUnreadCount();
    } catch (error) {
      console.error('Failed to mark message as read:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-end">
      <div className="bg-white rounded-t-2xl sm:rounded-lg shadow-2xl w-full sm:w-96 h-screen sm:h-[600px] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-600" />
            <h2 className="font-bold text-gray-900">Messages</h2>
            {unreadCount > 0 && (
              <span className="bg-red-500 text-white text-xs font-bold rounded-full px-2 py-1">
                {unreadCount}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('inbox')}
            className={`flex-1 py-3 px-4 font-medium text-sm transition-colors ${
              activeTab === 'inbox'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Inbox
          </button>
          <button
            onClick={() => setActiveTab('compose')}
            className={`flex-1 py-3 px-4 font-medium text-sm transition-colors ${
              activeTab === 'compose'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Compose
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {loading && (
            <div className="flex items-center justify-center h-full">
              <Loader className="w-6 h-6 text-blue-600 animate-spin" />
            </div>
          )}

          {activeTab === 'inbox' && !loading && (
            <div className="space-y-3">
              {messages.length === 0 ? (
                <p className="text-center text-gray-500 text-sm py-8">
                  No messages yet
                </p>
              ) : (
                messages.map((msg) => (
                  <div
                    key={msg.id}
                    onClick={() => !msg.read && handleMarkAsRead(msg.id)}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      msg.read
                        ? 'bg-gray-50 border-gray-200'
                        : 'bg-blue-50 border-blue-200'
                    } hover:bg-gray-100`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm text-gray-900 truncate">
                          {msg.sender.first_name} {msg.sender.last_name}
                        </p>
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {msg.content}
                        </p>
                      </div>
                      {!msg.read && (
                        <div className="w-2 h-2 rounded-full bg-blue-600 flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      {new Date(msg.sent_at).toLocaleDateString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'compose' && !loading && (
            <div className="space-y-4">
              {!selectedContact ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-700">
                    Select a contact:
                  </p>
                  {contacts.length === 0 ? (
                    <p className="text-center text-gray-500 text-sm py-8">
                      No contacts available
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {contacts.map((contact) => (
                        <button
                          key={contact.id}
                          onClick={() => setSelectedContact(contact)}
                          className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                        >
                          <p className="font-medium text-sm text-gray-900">
                            {contact.first_name} {contact.last_name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {contact.role}
                          </p>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <button
                    onClick={() => setSelectedContact(null)}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                     Back to contacts
                  </button>
                  <div className="p-3 rounded-lg bg-gray-50 border border-gray-200">
                    <p className="text-sm font-medium text-gray-900">
                      To: {selectedContact.first_name} {selectedContact.last_name}
                    </p>
                  </div>
                  <form onSubmit={handleSendMessage} className="space-y-3">
                    <textarea
                      value={messageContent}
                      onChange={(e) => setMessageContent(e.target.value)}
                      placeholder="Type your message..."
                      rows={5}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    />
                    <button
                      type="submit"
                      disabled={!messageContent.trim() || loading}
                      className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      Send
                    </button>
                  </form>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
