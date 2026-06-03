import React, { useEffect, useMemo, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  Bell,
  Download,
  FileText,
  Loader2,
  Lock,
  Palette,
  Save,
  Settings,
} from 'lucide-react';

import { WorkspaceShell } from '../components/workspace-shell';
import { Alert, Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { getCurrentUser, getStoredSession } from '../lib/django';
import { useAuth } from '../lib/hooks';
import {
  exportAuditLogs,
  getAuditLogs,
  getBrandingSettings,
  getNotificationSettings,
  updateBrandingSettings,
  updateNotificationSettings,
} from '../lib/api-service';
import { validators, validateForm } from '../lib/validation';

const TAB_ITEMS = [
  { id: 'branding', label: 'Branding', icon: Palette },
  { id: 'permissions', label: 'Permissions', icon: Lock },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'audit', label: 'Audit log', icon: FileText },
];

const Toggle = ({ checked, onChange }) => (
  <button
    type="button"
    onClick={onChange}
    className={`relative inline-flex h-7 w-12 items-center rounded-full transition ${checked ? 'bg-slate-950' : 'bg-slate-300'}`}
    role="switch"
    aria-checked={checked}
  >
    <span
      className={`inline-block h-5 w-5 rounded-full bg-white transition ${checked ? 'translate-x-6' : 'translate-x-1'}`}
    />
  </button>
);

const SectionCard = ({ title, description, children, className = '' }) => (
  <Card className={className}>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      {description ? <CardDescription>{description}</CardDescription> : null}
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);

export const AdminSettingsPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [session, setSession] = useState(() => getStoredSession());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('branding');
  const [saving, setSaving] = useState(false);
  const [auditLoading, setAuditLoading] = useState(false);

  const [schoolName, setSchoolName] = useState('');
  const [schoolEmail, setSchoolEmail] = useState('');
  const [primaryColor, setPrimaryColor] = useState('#0f172a');
  const [secondaryColor, setSecondaryColor] = useState('#1e293b');
  const [logoUrl, setLogoUrl] = useState('');
  const [formErrors, setFormErrors] = useState({});

  const [emailNotifications, setEmailNotifications] = useState(true);
  const [smsNotifications, setSmsNotifications] = useState(false);
  const [dailyDigest, setDailyDigest] = useState(true);
  const [auditLogs, setAuditLogs] = useState([]);

  useEffect(() => {
    if (!isAuthenticated) return;

    const load = async () => {
      setLoading(true);
      setError('');

      try {
        const current = await getCurrentUser();
        const activeSession = current || getStoredSession();

        if (!activeSession?.role) {
          setError('Unable to determine the current user role.');
          return;
        }

        if (!['admin', 'superadmin'].includes(activeSession.role)) {
          navigate(`/app/${activeSession.role}`);
          return;
        }

        setSession(activeSession);

        try {
          const brandingData = await getBrandingSettings();
          setSchoolName(brandingData.name || '');
          setSchoolEmail(brandingData.email || '');
          setPrimaryColor(brandingData.primary_color || '#0f172a');
          setSecondaryColor(brandingData.secondary_color || '#1e293b');
          setLogoUrl(brandingData.logo_url || '');
        } catch (brandingError) {
          console.error('Failed to load branding settings:', brandingError);
        }

        try {
          const notificationData = await getNotificationSettings();
          setEmailNotifications(notificationData.email !== false);
          setSmsNotifications(notificationData.sms === true);
          setDailyDigest(notificationData.daily_digest !== false);
        } catch (notificationError) {
          console.error('Failed to load notification settings:', notificationError);
        }
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.response?.data?.detail ||
          'Unable to load the settings workspace right now.'
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isAuthenticated, navigate]);

  const permissionsData = useMemo(
    () => [
      { role: 'Admin', permissions: ['Manage users', 'Reports', 'Settings', 'Audit review'] },
      { role: 'Teacher', permissions: ['Attendance', 'Grades', 'Assignments', 'Parent communication'] },
      { role: 'Bursar', permissions: ['Fees', 'Payments', 'Receipts', 'Finance reporting'] },
      { role: 'Student', permissions: ['Grades', 'Attendance', 'Assignments', 'Messages'] },
    ],
    []
  );

  const handleSaveBranding = async () => {
    const validationRules = {
      schoolName: (value) => validators.required(value, 'School name'),
      schoolEmail: validators.email,
      primaryColor: validators.hexColor,
      secondaryColor: validators.hexColor,
    };

    const { isValid, errors } = validateForm(
      { schoolName, schoolEmail, primaryColor, secondaryColor },
      validationRules
    );

    if (!isValid) {
      setFormErrors(errors);
      return;
    }

    setSaving(true);
    try {
      await updateBrandingSettings({
        name: schoolName,
        email: schoolEmail,
        primary_color: primaryColor,
        secondary_color: secondaryColor,
      });
      setFormErrors({});
    } catch (saveError) {
      setError(saveError.response?.data?.error || 'Failed to save branding settings.');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveNotifications = async () => {
    setSaving(true);
    try {
      await updateNotificationSettings({
        email: emailNotifications,
        sms: smsNotifications,
        daily_digest: dailyDigest,
      });
    } catch (saveError) {
      setError(saveError.response?.data?.error || 'Failed to save notification settings.');
    } finally {
      setSaving(false);
    }
  };

  const loadAuditTrail = async () => {
    setAuditLoading(true);
    try {
      const logs = await getAuditLogs({ limit: 20 });
      setAuditLogs(Array.isArray(logs) ? logs : []);
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Failed to load audit logs.');
    } finally {
      setAuditLoading(false);
    }
  };

  const handleExportAudit = async () => {
    try {
      const blob = await exportAuditLogs();
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      window.URL.revokeObjectURL(url);
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Failed to export audit logs.');
    }
  };

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  return (
    <WorkspaceShell
      session={session}
      role={session?.role || 'admin'}
      currentNav="settings"
      eyebrow="Admin Settings"
      title="Brand, permissions, and operating preferences"
      description="This is the command surface for how your school looks, how notifications behave, and how administrative actions are reviewed."
      actions={
        <Button variant="primary" onClick={activeTab === 'notifications' ? handleSaveNotifications : handleSaveBranding} disabled={saving}>
          <Save className="h-4 w-4" />
          {saving ? 'Saving...' : 'Save changes'}
        </Button>
      }
    >
      {loading ? (
        <div className="flex min-h-[320px] items-center justify-center">
          <div className="flex items-center gap-3 rounded-full bg-slate-950 px-5 py-3 text-white">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm font-medium">Loading settings workspace...</span>
          </div>
        </div>
      ) : error && !activeTab ? (
        <Alert variant="error">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5" />
            <div>
              <p className="font-medium">Settings error</p>
              <p className="mt-1 text-sm">{error}</p>
            </div>
          </div>
        </Alert>
      ) : (
        <div className="space-y-8">
          {error ? (
            <Alert variant="warning">
              <div className="flex items-start gap-3">
                <AlertCircle className="mt-0.5 h-5 w-5" />
                <div>
                  <p className="font-medium">Attention needed</p>
                  <p className="mt-1 text-sm">{error}</p>
                </div>
              </div>
            </Alert>
          ) : null}

          <div className="flex flex-wrap gap-3">
            {TAB_ITEMS.map((item) => {
              const Icon = item.icon;
              const active = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveTab(item.id)}
                  className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                    active ? 'bg-slate-950 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </button>
              );
            })}
          </div>

          {activeTab === 'branding' ? (
            <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
              <SectionCard title="School identity" description="Update the visible brand and contact details used across the experience.">
                <div className="space-y-5">
                  <div>
                    <label htmlFor="school-name" className="mb-2 block text-sm font-medium text-slate-950">School name</label>
                    <Input id="school-name" value={schoolName} onChange={(event) => setSchoolName(event.target.value)} className="h-12 rounded-2xl" />
                    {formErrors.schoolName ? <p className="mt-1 text-xs text-red-600">{formErrors.schoolName}</p> : null}
                  </div>
                  <div>
                    <label htmlFor="school-email" className="mb-2 block text-sm font-medium text-slate-950">School email</label>
                    <Input id="school-email" value={schoolEmail} onChange={(event) => setSchoolEmail(event.target.value)} className="h-12 rounded-2xl" />
                    {formErrors.schoolEmail ? <p className="mt-1 text-xs text-red-600">{formErrors.schoolEmail}</p> : null}
                  </div>
                  <div>
                    <label htmlFor="logo-url" className="mb-2 block text-sm font-medium text-slate-950">Logo URL</label>
                    <Input id="logo-url" value={logoUrl} onChange={(event) => setLogoUrl(event.target.value)} className="h-12 rounded-2xl" placeholder="https://example.com/logo.png" />
                  </div>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label htmlFor="primary-color" className="mb-2 block text-sm font-medium text-slate-950">Primary color</label>
                      <div className="flex gap-3">
                        <input aria-label="Primary color picker" type="color" value={primaryColor} onChange={(event) => setPrimaryColor(event.target.value)} className="h-12 w-14 rounded-2xl border border-slate-200 bg-white" />
                        <Input id="primary-color" value={primaryColor} onChange={(event) => setPrimaryColor(event.target.value)} className="h-12 rounded-2xl" />
                      </div>
                      {formErrors.primaryColor ? <p className="mt-1 text-xs text-red-600">{formErrors.primaryColor}</p> : null}
                    </div>
                    <div>
                      <label htmlFor="secondary-color" className="mb-2 block text-sm font-medium text-slate-950">Secondary color</label>
                      <div className="flex gap-3">
                        <input aria-label="Secondary color picker" type="color" value={secondaryColor} onChange={(event) => setSecondaryColor(event.target.value)} className="h-12 w-14 rounded-2xl border border-slate-200 bg-white" />
                        <Input id="secondary-color" value={secondaryColor} onChange={(event) => setSecondaryColor(event.target.value)} className="h-12 rounded-2xl" />
                      </div>
                      {formErrors.secondaryColor ? <p className="mt-1 text-xs text-red-600">{formErrors.secondaryColor}</p> : null}
                    </div>
                  </div>
                </div>
              </SectionCard>

              <SectionCard title="Brand preview" description="A quick visual check before you push changes live.">
                <div className="space-y-4">
                  <div className="rounded-[28px] p-6 text-white" style={{ backgroundColor: primaryColor }}>
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-sm text-white/70">Live preview</p>
                        <p className="mt-2 text-3xl font-semibold">{schoolName || 'Your school name'}</p>
                        <p className="mt-2 text-sm text-white/80">{schoolEmail || 'school@email.com'}</p>
                      </div>
                      {logoUrl ? (
                        <img src={logoUrl} alt="School logo preview" className="h-16 w-16 rounded-2xl bg-white/10 object-contain p-2" />
                      ) : (
                        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 text-sm font-semibold">
                          AE
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="rounded-[24px] border border-slate-200 px-5 py-5">
                    <p className="text-sm text-slate-500">Secondary accent</p>
                    <div className="mt-3 h-16 rounded-2xl" style={{ backgroundColor: secondaryColor }} />
                  </div>
                </div>
              </SectionCard>
            </div>
          ) : null}

          {activeTab === 'permissions' ? (
            <SectionCard title="Role permissions" description="A human-readable view of how the main operator roles are configured today.">
              <div className="grid gap-4 lg:grid-cols-2">
                {permissionsData.map((roleBlock) => (
                  <div key={roleBlock.role} className="rounded-[24px] border border-slate-200 bg-slate-50 px-5 py-5">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-lg font-semibold text-slate-950">{roleBlock.role}</p>
                      <Badge>{roleBlock.permissions.length} controls</Badge>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {roleBlock.permissions.map((permission) => (
                        <Badge key={permission} variant="primary">
                          {permission}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </SectionCard>
          ) : null}

          {activeTab === 'notifications' ? (
            <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
              <SectionCard title="Notification routing" description="Decide what reaches admins and when operational summaries are delivered.">
                <div className="space-y-4">
                  {[
                    ['Email notifications', 'Receive school events and operating alerts by email.', emailNotifications, () => setEmailNotifications((value) => !value)],
                    ['SMS notifications', 'Turn on text alerts for urgent payment or attendance events.', smsNotifications, () => setSmsNotifications((value) => !value)],
                    ['Daily digest', 'Send a summary of school activity at the end of each day.', dailyDigest, () => setDailyDigest((value) => !value)],
                  ].map(([title, description, checked, onChange]) => (
                    <div key={title} className="flex items-center justify-between gap-4 rounded-[24px] border border-slate-200 bg-slate-50 px-5 py-5">
                      <div>
                        <p className="font-medium text-slate-950">{title}</p>
                        <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
                      </div>
                      <Toggle checked={checked} onChange={onChange} />
                    </div>
                  ))}
                </div>
              </SectionCard>

              <SectionCard title="Notification stance" description="A quick summary of how the school is currently configured.">
                <div className="space-y-4">
                  <div className="rounded-[24px] bg-slate-950 p-5 text-white">
                    <p className="text-sm text-white/70">Current operating mode</p>
                    <p className="mt-2 text-2xl font-semibold">
                      {emailNotifications && dailyDigest ? 'Well covered' : 'Needs tuning'}
                    </p>
                    <p className="mt-3 text-sm leading-6 text-white/80">
                      Keep email and daily digest on for stronger leadership visibility, then add SMS only for genuinely urgent events.
                    </p>
                  </div>
                </div>
              </SectionCard>
            </div>
          ) : null}

          {activeTab === 'audit' ? (
            <SectionCard title="Audit trail" description="Review important administrative actions and export the trail when needed.">
              <div className="flex flex-wrap items-center gap-3">
                <Button variant="secondary" onClick={loadAuditTrail} disabled={auditLoading}>
                  {auditLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Settings className="h-4 w-4" />}
                  {auditLoading ? 'Refreshing...' : 'Refresh log'}
                </Button>
                <Button variant="secondary" onClick={handleExportAudit}>
                  <Download className="h-4 w-4" />
                  Export CSV
                </Button>
              </div>
              <div className="mt-6 space-y-3">
                {auditLogs.length > 0 ? (
                  auditLogs.map((log) => (
                    <div key={log.id} className="rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-medium text-slate-950">{log.action}</p>
                          <p className="mt-1 text-sm leading-6 text-slate-600">{log.details}</p>
                          <p className="mt-2 text-xs uppercase tracking-[0.12em] text-slate-500">
                            {log.user}  {log.timestamp}
                          </p>
                        </div>
                        <Badge>{log.user === 'System' ? 'System' : 'User'}</Badge>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-[24px] border border-dashed border-slate-300 px-5 py-10 text-center">
                    <p className="text-sm text-slate-500">No audit entries loaded yet.</p>
                  </div>
                )}
              </div>
            </SectionCard>
          ) : null}
        </div>
      )}
    </WorkspaceShell>
  );
};
