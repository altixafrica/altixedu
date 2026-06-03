import React, { useState, useEffect } from 'react';
import { WorldClassMessagingPanel } from '../components/world-class-messaging-panel';
import { AnnouncementPanel } from '../components/announcement-panel';
import { SiteHeader } from '../components/site-header';
import { SiteFooter } from '../components/site-footer';
import { Card, CardContent } from '../components/ui/card';

/**
 * MessagingDemoPage - Showcase real-time messaging and announcements
 * Testing ground for world-class communication features
 */
export const MessagingDemoPage = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'user2',
      sender_name: 'Jane Teacher',
      content: 'Hi! How are the new attendance features?',
      created_at: new Date(Date.now() - 5 * 60000).toISOString(),
      is_read: true,
    },
    {
      id: 2,
      sender: 'user1',
      sender_name: 'You',
      content: 'Excellent! Much easier to track now',
      created_at: new Date(Date.now() - 3 * 60000).toISOString(),
      is_read: true,
    },
    {
      id: 3,
      sender: 'user2',
      sender_name: 'Jane Teacher',
      content: 'Perfect!  Looking forward to using it in class',
      created_at: new Date(Date.now() - 1 * 60000).toISOString(),
      is_read: false,
    },
  ]);

  const [announcements, setAnnouncements] = useState([
    {
      id: 1,
      title: 'School Holiday Announcement',
      message: 'The school will be closed on May 15th for staff development day. All students and staff should prepare accordingly.',
      target_role: 'all',
      is_pinned: true,
      created_at: new Date().toISOString(),
      created_by: 'admin',
    },
    {
      id: 2,
      title: 'Final Exams Schedule',
      message: 'Exams will begin on June 1st. Students, make sure to submit your exam registrations by May 25th.',
      target_role: 'students',
      is_pinned: false,
      created_at: new Date(Date.now() - 24 * 60 * 60000).toISOString(),
      created_by: 'admin',
    },
  ]);

  const [isTyping, setIsTyping] = useState(false);
  const [typingTimeout, setTypingTimeout] = useState(null);

  const handleSendMessage = (text) => {
    const newMessage = {
      id: messages.length + 1,
      sender: 'user1',
      sender_name: 'You',
      content: text,
      created_at: new Date().toISOString(),
      is_read: false,
    };
    setMessages([...messages, newMessage]);

    // Simulate recipient typing
    setTimeout(() => {
      setIsTyping(true);
      setTimeout(() => {
        const replyMessage = {
          id: messages.length + 2,
          sender: 'user2',
          sender_name: 'Jane Teacher',
          content: ' Thanks for letting me know!',
          created_at: new Date().toISOString(),
          is_read: false,
        };
        setMessages((prev) => [...prev, replyMessage]);
        setIsTyping(false);
      }, 2000);
    }, 1500);
  };

  const handleSendAnnouncement = (announcementData) => {
    const newAnnouncement = {
      id: announcements.length + 1,
      ...announcementData,
      created_at: new Date().toISOString(),
      created_by: 'admin',
    };
    setAnnouncements([newAnnouncement, ...announcements]);
  };

  return (
    <>
      <SiteHeader />
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white py-12 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-12 text-center">
            <h1 className="text-5xl font-display font-bold text-slate-900 mb-3">
              Real-Time Communication
            </h1>
            <p className="text-xl text-slate-600">
              World-class messaging and announcements for your school
            </p>
          </div>

          {/* Two-Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Messaging Panel */}
            <Card className="shadow-2xl border-0">
              <CardContent className="p-0">
                <div className="h-[600px] bg-white rounded-lg overflow-hidden">
                  <WorldClassMessagingPanel
                    conversationId="conv1"
                    recipientName="Jane Teacher"
                    recipientStatus="online"
                    messages={messages}
                    isLoading={false}
                    isTyping={isTyping}
                    currentUserId="user1"
                    onSendMessage={handleSendMessage}
                    onMarkAsRead={() => {}}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Announcement Panel */}
            <div>
              <AnnouncementPanel
                isAdmin={true}
                announcements={announcements}
                onSubmit={handleSendAnnouncement}
              />
            </div>
          </div>

          {/* Features Grid */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="text-center">
              <CardContent className="pt-6">
                <div className="text-3xl mb-3"></div>
                <h3 className="font-display font-bold text-slate-900 mb-2">
                  Real-Time Messaging
                </h3>
                <p className="text-sm text-slate-600">
                  Instant delivery with typing indicators, read receipts, and online status
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="pt-6">
                <div className="text-3xl mb-3"></div>
                <h3 className="font-display font-bold text-slate-900 mb-2">
                  Role-Based Announcements
                </h3>
                <p className="text-sm text-slate-600">
                  Send targeted announcements to students, teachers, parents, or all users
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="pt-6">
                <div className="text-3xl mb-3"></div>
                <h3 className="font-display font-bold text-slate-900 mb-2">
                  WebSocket Powered
                </h3>
                <p className="text-sm text-slate-600">
                  Real-time delivery via Django Channels for zero latency communication
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Implementation Guide */}
          <Card className="mt-12 bg-slate-900 text-white border-0">
            <CardContent className="pt-8 pb-8">
              <h2 className="text-2xl font-display font-bold mb-4"> Implementation Guide</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                <div>
                  <h3 className="font-semibold mb-2 text-blue-300">Backend Setup (Django)</h3>
                  <pre className="bg-slate-950 p-3 rounded text-xs overflow-x-auto text-green-400">
{`# Start with Daphne ASGI server
daphne -b 0.0.0.0 -p 8000 \\
  altixedu.asgi:application

# Uses WebSocket routing at /ws/messages/
# Handles real-time message delivery
# Manages typing indicators & read receipts`}
                  </pre>
                </div>
                <div>
                  <h3 className="font-semibold mb-2 text-green-300">Frontend Integration (React)</h3>
                  <pre className="bg-slate-950 p-3 rounded text-xs overflow-x-auto text-yellow-400">
{`import { WorldClassMessagingPanel } 
  from '@/components/world-class-messaging-panel'
import { AnnouncementPanel } 
  from '@/components/announcement-panel'

// Add to your dashboard:
<WorldClassMessagingPanel />
<AnnouncementPanel isAdmin={true} />`}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
      <SiteFooter />
    </>
  );
};
