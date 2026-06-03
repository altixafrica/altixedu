import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Loader, Check, CheckCheck, Circle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/form';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { MessageSkeleton } from './skeleton-loaders';

/**
 * WorldClassMessagingPanel - Premium real-time messaging UI
 * 
 * Features:
 * - WebSocket real-time message delivery
 * - Typing indicators
 * - Read receipts (delivered, read)
 * - Online/offline status badges
 * - Message grouping by sender and time
 * - Smooth animations and transitions
 * - Playfair Display headings for elegance
 */
export const WorldClassMessagingPanel = ({
  conversationId,
  recipientName = "Recipient",
  recipientStatus = "online",
  messages = [],
  isLoading = false,
  isTyping = false,
  currentUserId,
  onSendMessage,
  onMarkAsRead,
}) => {
  const [messageText, setMessageText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to latest message
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!messageText.trim()) return;

    setIsSending(true);
    try {
      await onSendMessage(messageText);
      setMessageText('');
      textareaRef.current?.focus();
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSendMessage(e);
    }
  };

  // Group messages by sender and time
  const groupedMessages = messages.reduce((acc, msg, idx) => {
    const lastGroup = acc[acc.length - 1];
    const timeDiff = lastGroup && new Date(msg.created_at) - new Date(lastGroup.messages[0].created_at);
    const isSameSender = lastGroup && lastGroup.senderId === msg.sender;
    const isWithinMinute = timeDiff && timeDiff < 60000;

    if (isSameSender && isWithinMinute) {
      lastGroup.messages.push(msg);
    } else {
      acc.push({
        senderId: msg.sender,
        senderName: msg.sender_name,
        messages: [msg],
      });
    }
    return acc;
  }, []);

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-slate-50 to-white rounded-2xl shadow-xl overflow-hidden">
      {/* Header - Elegant with online status */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white px-6 py-5 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-display font-bold">
              {recipientName}
            </h1>
            <div className="flex items-center gap-2 mt-1">
              <Circle
                className={`w-2 h-2 ${
                  recipientStatus === 'online'
                    ? 'fill-green-400 text-green-400'
                    : 'fill-slate-400 text-slate-400'
                }`}
              />
              <span className="text-sm text-slate-300">
                {recipientStatus === 'online' ? 'Active now' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {isLoading ? (
          <MessageSkeleton count={3} />
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="text-4xl mb-3"></div>
            <p className="text-slate-500 font-medium">No messages yet</p>
            <p className="text-sm text-slate-400">Start a conversation</p>
          </div>
        ) : (
          groupedMessages.map((group, idx) => {
            const isCurrentUser = group.senderId === currentUserId;
            const isFirstInGroup = idx === 0 || groupedMessages[idx - 1].senderId !== group.senderId;

            return (
              <div key={idx} className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex gap-3 max-w-xs ${isCurrentUser ? 'flex-row-reverse' : 'flex-row'}`}>
                  {/* Avatar on first message of group */}
                  {isFirstInGroup && (
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0 ${
                        isCurrentUser
                          ? 'bg-gradient-to-br from-blue-500 to-brand-600'
                          : 'bg-gradient-to-br from-purple-500 to-pink-500'
                      }`}
                    >
                      {group.senderName?.charAt(0).toUpperCase()}
                    </div>
                  )}
                  {!isFirstInGroup && <div className="w-8 flex-shrink-0" />}

                  {/* Messages */}
                  <div className="space-y-1">
                    {group.messages.map((msg, msgIdx) => (
                      <div
                        key={msg.id}
                        className={`rounded-2xl px-4 py-2 backdrop-blur-sm transition-all duration-200 animate-fade-in ${
                          isCurrentUser
                            ? 'bg-gradient-to-br from-blue-600 to-brand-600 text-white rounded-br-none'
                            : 'bg-white text-slate-900 rounded-bl-none border border-slate-200 shadow-sm'
                        }`}
                      >
                        <p className="text-sm leading-relaxed">{msg.content}</p>
                      </div>
                    ))}
                    
                    {/* Message Status for last message in group */}
                    {isCurrentUser && group.messages.length > 0 && (
                      <div className="flex items-center gap-1 mt-1 ml-auto">
                        <span className="text-xs text-slate-500">
                          {new Date(group.messages[group.messages.length - 1].created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                        {group.messages[group.messages.length - 1].is_read ? (
                          <CheckCheck className="w-3 h-3 text-blue-400" />
                        ) : (
                          <Check className="w-3 h-3 text-slate-400" />
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
              ?
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-none px-4 py-2 flex gap-1">
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Elegant with gradient */}
      <div className="border-t border-slate-200 bg-white px-6 py-4">
        <form onSubmit={handleSendMessage} className="flex gap-3">
          <textarea
            ref={textareaRef}
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message... (Ctrl+Enter to send)"
            rows={1}
            className="flex-1 px-4 py-2 border border-slate-300 rounded-full focus:border-brand-600 focus:ring-2 focus:ring-brand-600/20 focus:outline-none resize-none text-sm"
            disabled={isSending}
          />
          <button
            type="submit"
            disabled={isSending || !messageText.trim()}
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-brand-600 text-white rounded-full hover:from-blue-700 hover:to-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2 font-medium flex-shrink-0"
          >
            {isSending ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default WorldClassMessagingPanel;
