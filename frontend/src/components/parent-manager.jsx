import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Link as LinkIcon } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { LoadingButton } from './quick-wins-animations';
import apiClient from '../lib/api-client';

export const ParentManager = () => {
  const [parents, setParents] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [selectedParent, setSelectedParent] = useState(null);
  const [credentials, setCredentials] = useState(null);
  const [showCredentials, setShowCredentials] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });
  const [linkData, setLinkData] = useState({
    student_id: '',
    relationship: 'parent',
    is_primary: false,
  });

  useEffect(() => {
    fetchParents();
    fetchStudents();
  }, []);

  const fetchParents = async () => {
    try {
      const response = await apiClient.get('/api/users/?role=parent');
      setParents(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching parents:', error);
    }
  };

  const fetchStudents = async () => {
    try {
      const response = await apiClient.get('/api/students/');
      setStudents(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching students:', error);
    }
  };

  const handleCreateParent = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const password = Math.random().toString(36).slice(-12);
      const username = formData.email.split('@')[0] + '_parent';

      const userData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        username: username,
        password: password,
        role: 'parent',
        phone: formData.phone,
      };

      const response = await apiClient.post('/api/users/', userData);

      setCredentials({
        email: formData.email,
        username: username,
        password: password,
        role: 'Parent',
      });
      setShowCredentials(true);

      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
      });
      setShowForm(false);

      fetchParents();
    } catch (error) {
      console.error('Error creating parent:', error);
      alert('Error creating parent: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleLinkParentToStudent = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.post('/api/parent-student-links/', {
        parent: selectedParent.id,
        student: parseInt(linkData.student_id),
        relationship: linkData.relationship,
        is_primary: linkData.is_primary,
        receives_progress_reports: true,
        can_view_grades: true,
        can_authorize_absence: false,
      });

      setLinkData({
        student_id: '',
        relationship: 'parent',
        is_primary: false,
      });
      setShowLinkModal(false);
      setSelectedParent(null);

      alert('Parent linked to student successfully!');
    } catch (error) {
      console.error('Error linking parent to student:', error);
      alert('Error linking parent to student: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteParent = async (parentId) => {
    if (!window.confirm('Are you sure you want to delete this parent?')) return;
    
    try {
      await apiClient.delete(`/api/users/${parentId}/`);
      fetchParents();
    } catch (error) {
      console.error('Error deleting parent:', error);
      alert('Error deleting parent');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-display font-bold text-slate-900">Parent Management</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 text-white px-4 py-2 hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Parent
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <Card className="border-2 border-blue-200">
          <CardContent className="pt-6">
            <form onSubmit={handleCreateParent} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">First Name</label>
                  <input
                    type="text"
                    required
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Mary"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
                  <input
                    type="text"
                    required
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Adeyemi"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="parent@email.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="+234..."
                />
              </div>
              <div className="flex gap-3">
                <LoadingButton loading={loading} type="submit" className="bg-blue-600 hover:bg-blue-700">
                  Create Parent
                </LoadingButton>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Credentials Modal */}
      {showCredentials && credentials && (
        <Card className="border-2 border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-green-900"> Parent Created Successfully!</h3>
                <button onClick={() => setShowCredentials(false)} className="text-green-600"></button>
              </div>
              <div className="bg-white p-4 rounded-lg space-y-3 font-mono text-sm">
                <div>
                  <span className="font-semibold text-slate-600">Email:</span>
                  <span className="ml-2 text-slate-900">{credentials.email}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-600">Username:</span>
                  <span className="ml-2 text-slate-900">{credentials.username}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-600">Password:</span>
                  <span className="ml-2 text-slate-900 tracking-wider">{credentials.password}</span>
                </div>
              </div>
              <button
                onClick={() => {
                  const text = `Email: ${credentials.email}\nUsername: ${credentials.username}\nPassword: ${credentials.password}`;
                  navigator.clipboard.writeText(text);
                  alert('Credentials copied!');
                }}
                className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                Copy Credentials
              </button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Link Modal */}
      {showLinkModal && selectedParent && (
        <Card className="border-2 border-purple-200">
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Link to Student</h3>
            <form onSubmit={handleLinkParentToStudent} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Student</label>
                <select
                  required
                  value={linkData.student_id}
                  onChange={(e) => setLinkData({ ...linkData, student_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                >
                  <option value="">Select a student</option>
                  {students.map((student) => (
                    <option key={student.id} value={student.id}>
                      {student.first_name} {student.last_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Relationship</label>
                <select
                  value={linkData.relationship}
                  onChange={(e) => setLinkData({ ...linkData, relationship: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                >
                  <option value="mother">Mother</option>
                  <option value="father">Father</option>
                  <option value="guardian">Guardian</option>
                  <option value="grandparent">Grandparent</option>
                  <option value="sibling">Sibling</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_primary"
                  checked={linkData.is_primary}
                  onChange={(e) => setLinkData({ ...linkData, is_primary: e.target.checked })}
                  className="w-4 h-4 rounded"
                />
                <label htmlFor="is_primary" className="text-sm text-slate-700">
                  Make this the primary contact
                </label>
              </div>
              <div className="flex gap-3">
                <LoadingButton loading={loading} type="submit" className="bg-purple-600 hover:bg-purple-700">
                  Link Parent
                </LoadingButton>
                <button
                  type="button"
                  onClick={() => {
                    setShowLinkModal(false);
                    setSelectedParent(null);
                  }}
                  className="px-4 py-2 rounded-lg border border-slate-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Parents List */}
      <div className="grid gap-4">
        {parents.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center text-slate-500">
              No parents created yet. Click "Add Parent" to get started.
            </CardContent>
          </Card>
        ) : (
          parents.map((parent) => (
            <Card key={parent.id}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      {parent.first_name} {parent.last_name}
                    </h3>
                    <p className="text-sm text-slate-600">{parent.email}</p>
                    {parent.phone && (
                      <p className="text-sm text-slate-600">{parent.phone}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setSelectedParent(parent);
                        setShowLinkModal(true);
                      }}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Link to student"
                    >
                      <LinkIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDeleteParent(parent.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};
