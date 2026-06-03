import React, { useEffect, useMemo, useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  Download,
  Edit2,
  Loader2,
  Plus,
  Search,
  Trash2,
  Upload,
  Users,
  X,
} from 'lucide-react';

import { WorkspaceShell } from '../components/workspace-shell';
import { Alert, Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { getCurrentUser, getStoredSession } from '../lib/django';
import { useAuth } from '../lib/hooks';
import { bulkImportUsers, createUser, deleteUser, getUsers, updateUser } from '../lib/api-service';
import { validators, validateForm } from '../lib/validation';
import { BursarManager } from '../components/bursar-manager';
import { ParentManager } from '../components/parent-manager';
import { ClassroomAssignment } from '../components/classroom-assignment';

const TAB_LABELS = {
  students: 'Students',
  teachers: 'Teachers',
  bursars: 'Bursars',
  parents: 'Parents',
  classrooms: 'Classrooms',
  import: 'Bulk Import',
};

const defaultFormState = {
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  role: 'student',
  phone: '',
  classroom: '',
};

const SectionCard = ({ title, description, children, className = '' }) => (
  <Card className={className}>
    <CardHeader>
      <CardTitle>{title}</CardTitle>
      {description ? <CardDescription>{description}</CardDescription> : null}
    </CardHeader>
    <CardContent>{children}</CardContent>
  </Card>
);

export const UserManagementPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [session, setSession] = useState(() => getStoredSession());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('students');
  const [saving, setSaving] = useState(false);
  const [users, setUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState(defaultFormState);
  const [formErrors, setFormErrors] = useState({});
  const [importFile, setImportFile] = useState(null);

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
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.response?.data?.detail ||
          'Unable to load user management right now.'
        );
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (activeTab === 'import' || !isAuthenticated) return;

    const loadTabUsers = async () => {
      try {
        const role = activeTab === 'students' ? 'student' : 'teacher';
        const data = await getUsers(role);
        setUsers(Array.isArray(data) ? data : []);
      } catch (requestError) {
        setUsers([]);
        setError(requestError.response?.data?.error || `Failed to load ${activeTab}.`);
      }
    };

    loadTabUsers();
  }, [activeTab, isAuthenticated]);

  const filteredUsers = useMemo(
    () =>
      users.filter((user) =>
        `${user.first_name} ${user.last_name} ${user.email} ${user.username}`
          .toLowerCase()
          .includes(searchQuery.toLowerCase())
      ),
    [searchQuery, users]
  );

  const statCards = useMemo(
    () => [
      {
        label: 'Students',
        value: activeTab === 'students' ? filteredUsers.length : users.filter((user) => user.role === 'student').length,
      },
      {
        label: 'Teachers',
        value: activeTab === 'teachers' ? filteredUsers.length : users.filter((user) => user.role === 'teacher').length,
      },
      {
        label: 'Ready for import',
        value: importFile ? '1 file' : 'No file',
      },
    ],
    [activeTab, filteredUsers.length, importFile, users]
  );

  const openCreateModal = () => {
    setEditingUser(null);
    setFormErrors({});
    setFormData({
      ...defaultFormState,
      role: activeTab === 'students' ? 'student' : 'teacher',
    });
    setShowModal(true);
  };

  const openEditModal = (user) => {
    setEditingUser(user);
    setFormErrors({});
    setFormData({
      ...defaultFormState,
      ...user,
    });
    setShowModal(true);
  };

  const handleSaveUser = async () => {
    const validationRules = {
      first_name: (value) => validators.required(value, 'First name'),
      last_name: (value) => validators.required(value, 'Last name'),
      email: validators.email,
      username: validators.username,
      classroom: activeTab === 'students' ? validators.classroom : () => '',
      phone: activeTab === 'teachers' ? validators.phone : () => '',
    };

    const { isValid, errors } = validateForm(formData, validationRules);
    if (!isValid) {
      setFormErrors(errors);
      return;
    }

    setSaving(true);
    try {
      const payload = {
        ...formData,
        role: activeTab === 'students' ? 'student' : 'teacher',
      };

      if (editingUser) {
        await updateUser(editingUser.id, payload);
      } else {
        await createUser(payload);
      }

      setShowModal(false);
      setActiveTab((current) => current);
      const refreshedUsers = await getUsers(activeTab === 'students' ? 'student' : 'teacher');
      setUsers(Array.isArray(refreshedUsers) ? refreshedUsers : []);
    } catch (requestError) {
      setError(
        requestError.response?.data?.error ||
        requestError.response?.data?.detail ||
        'Failed to save the user record.'
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteUser = async (userId, userName) => {
    if (!window.confirm(`Delete ${userName}?`)) return;

    try {
      await deleteUser(userId);
      setUsers((currentUsers) => currentUsers.filter((user) => user.id !== userId));
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Failed to delete user.');
    }
  };

  const handleFileImport = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setImportFile(file);
    setSaving(true);

    try {
      await bulkImportUsers(file, activeTab === 'teachers' ? 'teacher' : 'student');
    } catch (requestError) {
      setError(
        requestError.response?.data?.error ||
        requestError.response?.data?.detail ||
        'Failed to import the selected file.'
      );
    } finally {
      setSaving(false);
    }
  };

  if (!isAuthenticated) {
    return <Navigate replace to="/login" />;
  }

  return (
    <WorkspaceShell
      session={session}
      role={session?.role || 'admin'}
      currentNav="users"
      eyebrow="User Operations"
      title="People, identity, and onboarding flow"
      description="Manage students and teachers with a calmer operational surface for searching, editing, and structured bulk import."
      actions={
        activeTab !== 'import' ? (
          <Button variant="primary" onClick={openCreateModal}>
            <Plus className="h-4 w-4" />
            Add {activeTab === 'students' ? 'student' : 'teacher'}
          </Button>
        ) : null
      }
    >
      {loading ? (
        <div className="flex min-h-[320px] items-center justify-center">
          <div className="flex items-center gap-3 rounded-full bg-slate-950 px-5 py-3 text-white">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span className="text-sm font-medium">Loading user operations...</span>
          </div>
        </div>
      ) : error && !activeTab ? (
        <Alert variant="error">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5" />
            <div>
              <p className="font-medium">User management error</p>
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

          <div className="grid gap-4 md:grid-cols-3">
            {statCards.map((card) => (
              <div key={card.label} className="rounded-[24px] border border-slate-200 bg-slate-50 px-5 py-5">
                <p className="text-sm text-slate-500">{card.label}</p>
                <p className="mt-2 text-3xl font-semibold text-slate-950">{card.value}</p>
              </div>
            ))}
          </div>

          <div className="flex flex-wrap gap-3">
            {Object.entries(TAB_LABELS).map(([id, label]) => (
              <button
                key={id}
                type="button"
                onClick={() => setActiveTab(id)}
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                  activeTab === id ? 'bg-slate-950 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                <Users className="h-4 w-4" />
                {label}
              </button>
            ))}
          </div>

          {activeTab === 'bursars' ? (
            <BursarManager />
          ) : activeTab === 'parents' ? (
            <ParentManager />
          ) : activeTab === 'classrooms' ? (
            <ClassroomAssignment />
          ) : activeTab !== 'import' ? (
            <SectionCard
              title={`${TAB_LABELS[activeTab]} directory`}
              description="Search the current roster, review user identity details, and make changes without losing list context."
            >
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="relative w-full max-w-xl">
                  <Search className="pointer-events-none absolute left-4 top-3.5 h-4 w-4 text-slate-400" />
                  <Input
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    className="h-12 rounded-2xl pl-11"
                    placeholder={`Search ${activeTab} by name, email, or username`}
                  />
                </div>
              </div>

              <div className="mt-6 overflow-x-auto">
                <table className="w-full min-w-[760px] text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left">
                      <th className="pb-3 font-medium text-slate-500">Name</th>
                      <th className="pb-3 font-medium text-slate-500">Email</th>
                      <th className="pb-3 font-medium text-slate-500">Username</th>
                      <th className="pb-3 font-medium text-slate-500">{activeTab === 'students' ? 'Classroom' : 'Phone'}</th>
                      <th className="pb-3 font-medium text-slate-500">Status</th>
                      <th className="pb-3 text-right font-medium text-slate-500">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.length > 0 ? (
                      filteredUsers.map((user) => (
                        <tr key={user.id} className="border-b border-slate-100">
                          <td className="py-4">
                            <p className="font-medium text-slate-950">{user.first_name} {user.last_name}</p>
                          </td>
                          <td className="py-4 text-slate-600">{user.email}</td>
                          <td className="py-4 text-slate-600">{user.username}</td>
                          <td className="py-4 text-slate-600">{activeTab === 'students' ? user.classroom || 'N/A' : user.phone || 'N/A'}</td>
                          <td className="py-4">
                            <Badge variant={user.status === 'active' ? 'success' : 'default'}>
                              {user.status || 'active'}
                            </Badge>
                          </td>
                          <td className="py-4">
                            <div className="flex justify-end gap-2">
                              <Button variant="ghost" size="sm" onClick={() => openEditModal(user)}>
                                <Edit2 className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteUser(user.id, `${user.first_name} ${user.last_name}`)}
                              >
                                <Trash2 className="h-4 w-4 text-red-600" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="6" className="py-12 text-center text-slate-500">
                          No matching users found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </SectionCard>
          ) : (
            <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
              <SectionCard title="Bulk import" description="Upload structured rosters so onboarding can happen in fewer clicks.">
                <label className="block cursor-pointer rounded-[28px] border-2 border-dashed border-slate-300 px-6 py-12 text-center transition hover:border-slate-400">
                  <Upload className="mx-auto h-10 w-10 text-slate-400" />
                  <p className="mt-4 font-medium text-slate-950">Drop or choose a CSV file</p>
                  <p className="mt-2 text-sm text-slate-500">Expected columns: first_name, last_name, email, username, classroom</p>
                  <input type="file" accept=".csv" className="hidden" onChange={handleFileImport} disabled={saving} />
                </label>
                {importFile ? (
                  <div className="rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-4">
                    <p className="font-medium text-slate-950">{importFile.name}</p>
                    <p className="mt-1 text-sm text-slate-500">{saving ? 'Import in progress...' : 'File ready for import processing.'}</p>
                  </div>
                ) : null}
              </SectionCard>

              <SectionCard title="Template guidance" description="Keep source files clean so onboarding lands smoothly.">
                <div className="rounded-[24px] bg-slate-950 p-5 text-white">
                  <p className="text-sm text-white/70">Suggested CSV header</p>
                  <pre className="mt-4 overflow-x-auto text-sm text-white/90">
first_name,last_name,email,username,classroom
John,Doe,john@school.edu,johndoe,SS 3A
Jane,Smith,jane@school.edu,janesmith,SS 3B
                  </pre>
                </div>
                <div className="mt-4">
                  <Button variant="secondary">
                    <Download className="h-4 w-4" />
                    Download template
                  </Button>
                </div>
              </SectionCard>
            </div>
          )}
        </div>
      )}

      {showModal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
          <Card className="w-full max-w-xl">
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <div>
                <CardTitle>{editingUser ? 'Edit user' : `Add ${activeTab === 'students' ? 'student' : 'teacher'}`}</CardTitle>
                <CardDescription>Update core identity details without leaving the roster.</CardDescription>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setShowModal(false)}>
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-950">First name</label>
                  <Input value={formData.first_name} onChange={(event) => setFormData((current) => ({ ...current, first_name: event.target.value }))} className="h-12 rounded-2xl" />
                  {formErrors.first_name ? <p className="mt-1 text-xs text-red-600">{formErrors.first_name}</p> : null}
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-950">Last name</label>
                  <Input value={formData.last_name} onChange={(event) => setFormData((current) => ({ ...current, last_name: event.target.value }))} className="h-12 rounded-2xl" />
                  {formErrors.last_name ? <p className="mt-1 text-xs text-red-600">{formErrors.last_name}</p> : null}
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-950">Email</label>
                <Input value={formData.email} onChange={(event) => setFormData((current) => ({ ...current, email: event.target.value }))} className="h-12 rounded-2xl" />
                {formErrors.email ? <p className="mt-1 text-xs text-red-600">{formErrors.email}</p> : null}
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-950">Username</label>
                <Input value={formData.username} onChange={(event) => setFormData((current) => ({ ...current, username: event.target.value }))} className="h-12 rounded-2xl" />
                {formErrors.username ? <p className="mt-1 text-xs text-red-600">{formErrors.username}</p> : null}
              </div>
              {activeTab === 'students' ? (
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-950">Classroom</label>
                  <Input value={formData.classroom} onChange={(event) => setFormData((current) => ({ ...current, classroom: event.target.value }))} className="h-12 rounded-2xl" />
                  {formErrors.classroom ? <p className="mt-1 text-xs text-red-600">{formErrors.classroom}</p> : null}
                </div>
              ) : (
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-950">Phone</label>
                  <Input value={formData.phone} onChange={(event) => setFormData((current) => ({ ...current, phone: event.target.value }))} className="h-12 rounded-2xl" />
                  {formErrors.phone ? <p className="mt-1 text-xs text-red-600">{formErrors.phone}</p> : null}
                </div>
              )}
              <div className="flex gap-3 pt-2">
                <Button fullWidth variant="secondary" onClick={() => setShowModal(false)} disabled={saving}>
                  Cancel
                </Button>
                <Button fullWidth variant="primary" onClick={handleSaveUser} disabled={saving}>
                  {saving ? 'Saving...' : 'Save user'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </WorkspaceShell>
  );
};
