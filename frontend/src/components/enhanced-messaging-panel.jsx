import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, MessageSquare, X, Loader, Check, CheckCheck, Zap } from 'lucide-react';
import {
  sendMessage,
  getInbox,
  getMessageContacts,
  markMessageAsRead,
  getUnreadCount,
} from '../lib/django';
import { useError } from './error-display';
import { formatErrorForDisplay } from '../lib/error-handler';
import { useRealtimeMessaging, useOnlineUsers, useTypingIndicators } from '../hooks/use-realtime-messaging';

export const EnhancedMessagingPanel = ({ isOpen, onClose, currentUser }) => {
  const [activeTab, setActiveTab] = useState('inbox');
  const [messages, setMessages] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);
  const [messageContent, setMessageContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [sentMessages, setSentMessages] = useState(new Set());
  const [readMessages, setReadMessages] = useState(new Set());
  const messagesEndRef = useRef(null);
  const { addError } = useError();
  const { onlineUsers, handleUserStatus } = useOnlineUsers();
  const { typingUsers, handleTyping, isTyping } = useTypingIndicators();

  // Real-time messaging
  const { connected, sendMessage: wsSendMessage, sendTypingIndicator, sendReadReceipt } = useRealtimeMessaging(
    (msg) => {
      // New message received
      setMessages((prev) => [...prev, msg]);
      // Scroll to bottom
      setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
    },
    handleTyping,
    (receipt) => {
      // Mark message as read
      setReadMessages((prev) => new Set([...prev, receipt.message_id]));
    },
    handleUserStatus
  );

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  }, []);

  // Load initial messages
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
      scrollToBottom();
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

    const trimmedContent = messageContent.trim();
    const messageId = `temp_${Date.now()}`;
    
    setLoading(true);
    setSentMessages((prev) => new Set([...prev, messageId]));
    setMessageContent('');

    try {
      // Try real-time first
      if (connected) {
        wsSendMessage(selectedContact.id, trimmedContent);
      } else {
        // Fall back to HTTP
        await sendMessage(selectedContact.id, trimmedContent);
      }
      
      await loadMessages();
      await loadUnreadCount();
    } catch (error) {
      const formatted = formatErrorForDisplay(error);
      addError(formatted.message);
      setSentMessages((prev) => {
        const newSet = new Set(prev);
        newSet.delete(messageId);
        return newSet;
      });
      setMessageContent(trimmedContent);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (messageId) => {
    try {
      sendReadReceipt(messageId);
      await markMessageAsRead(messageId);
      await loadMessages();
      await loadUnreadCount();
    } catch (error) {
      console.error('Failed to mark message as read:', error);
    }
  };

  const handleTextChange = useCallback(() => {
    if (selectedContact && connected) {
      sendTypingIndicator(selectedContact.id, true);
      // Clear typing status after 2 seconds of inactivity
      const timeout = setTimeout(() => {
        sendTypingIndicator(selectedContact.id, false);
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [selectedContact, connected, sendTypingIndicator]);

  const isContactOnline = (contactId) => {
    return onlineUsers.has(contactId);
  };

  const isContactTyping = (contactId) => {
    return isTyping(contactId);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-end">
      <div className="bg-white rounded-t-2xl sm:rounded-lg shadow-2xl w-full sm:w-96 h-screen sm:h-[600px] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-center gap-2">
            <div className="relative">
              <MessageSquare className="w-5 h-5 text-blue-600" />
              {unreadCount > 0 && (
                <Zap className="absolute -top-1 -right-1 w-3 h-3 text-red-500" />
              )}
            </div>
            <h2 className="font-bold text-gray-900">Messages</h2>
            {unreadCount > 0 && (
              <span className="bg-red-500 text-white text-xs font-bold rounded-full px-2 py-1 animate-pulse">
                {unreadCount}
              </span>
            )}
            {connected && (
              <span className="text-xs text-green-600 font-medium flex items-center gap-1">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                Live
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
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
          {loading && activeTab === 'inbox' && (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <MessageSkeleton key={i} />
              ))}
            </div>
          )}

          {activeTab === 'inbox' && !loading && (
            <div className="space-y-3">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 text-sm py-8">
                  <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No messages yet</p>
                </div>
              ) : (
                messages.map((msg) => (
                  <MessageItem
                    key={msg.id}
                    message={msg}
                    onMarkRead={() => handleMarkAsRead(msg.id)}
                    isSent={sentMessages.has(msg.id)}
                    isRead={readMessages.has(msg.id) || msg.read}
                    isContactOnline={isContactOnline(msg.sender_id)}
                  />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          )}

          {activeTab === 'compose' && !loading && (
            <div className="space-y-4">
              {!selectedContact ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-700">Select a contact:</p>
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
                          className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-blue-50 hover:border-blue-300 transition-all group"
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium text-sm text-gray-900">
                                {contact.first_name} {contact.last_name}
                              </p>
                              <p className="text-xs text-gray-500">{contact.role}</p>
                            </div>
                            {isContactOnline(contact.id) && (
                              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  <button
                    onClick={() => setSelectedContact(null)}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
                  >
                     Back to contacts
                  </button>
                  <div className="p-3 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          To: {selectedContact.first_name} {selectedContact.last_name}
                        </p>
                        <p className="text-xs text-gray-500">{selectedContact.role}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {isContactOnline(selectedContact.id) && (
                          <span className="flex items-center gap-1 text-xs text-green-600">
                            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                            Online
                          </span>
                        )}
                        {isContactTyping(selectedContact.id) && (
                          <span className="text-xs text-blue-600 font-medium flex items-center gap-1">
                            Typing
                            <span className="inline-flex gap-1">
                              <span className="w-1 h-1 bg-blue-600 rounded-full animate-bounce" />
                              <span className="w-1 h-1 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                              <span className="w-1 h-1 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                            </span>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <form onSubmit={handleSendMessage} className="space-y-3">
                    <textarea
                      value={messageContent}
                      onChange={(e) => {
                        setMessageContent(e.target.value);
                        handleTextChange();
                      }}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && e.ctrlKey) {
                          handleSendMessage(e);
                        }
                      }}
                      placeholder="Type your message... (Ctrl+Enter to send)"
                      rows={5}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
                    />
                    <div className="text-xs text-gray-500">
                      Ctrl+Enter to send quickly
                    </div>
                    <button
                      type="submit"
                      disabled={!messageContent.trim() || loading || !connected}
                      className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-2 rounded-lg transition-all flex items-center justify-center gap-2 transform hover:scale-105 active:scale-95"
                    >
                      {loading ? (
                        <Loader className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                      {loading ? 'Sending...' : 'Send'}
                    </button>
                    {!connected && (
                      <div className="text-xs text-amber-600 bg-amber-50 p-2 rounded text-center">
                        Reconnecting... Messages will send when connection restored
                      </div>
                    )}
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

// Skeleton loader for messages
const MessageSkeleton = () => (
  <div className="p-3 rounded-lg bg-gray-100 animate-pulse">
    <div className="h-4 bg-gray-300 rounded w-3/4 mb-2" />
    <div className="h-3 bg-gray-300 rounded w-full" />
  </div>
);

// Individual message item
const MessageItem = ({ message, onMarkRead, isSent, isRead, isContactOnline }) => (
  <div
    onClick={() => !message.read && onMarkRead()}
    className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
      message.read ? 'bg-gray-50 border-gray-200' : 'bg-blue-50 border-blue-200'
    }`}
  >
    <div className="flex items-start justify-between gap-2">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="font-medium text-sm text-gray-900 truncate">
            {message.sender.first_name} {message.sender.last_name}
          </p>
          {isContactOnline && (
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse flex-shrink-0" />
          )}
        </div>
        <p className="text-sm text-gray-600 line-clamp-2">{message.content}</p>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        {isSent && (
          isRead ? (
            <CheckCheck className="w-4 h-4 text-blue-600" title="Read" />
          ) : (
            <Check className="w-4 h-4 text-gray-400" title="Sent" />
          )
        )}
        {!message.read && (
          <div className="w-2 h-2 rounded-full bg-blue-600" />
        )}
      </div>
    </div>
    <p className="text-xs text-gray-500 mt-2">
      {new Date(message.sent_at).toLocaleDateString()} {new Date(message.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
    </p>
  </div>
);
