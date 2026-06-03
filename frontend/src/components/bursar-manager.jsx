import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Eye, EyeOff } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { LoadingButton } from './quick-wins-animations';
import apiClient from '../lib/api-client';

export const BursarManager = () => {
  const [bursars, setBursars] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [showCredentials, setShowCredentials] = useState(null);
  const [credentials, setCredentials] = useState(null);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });

  useEffect(() => {
    fetchBursars();
  }, []);

  const fetchBursars = async () => {
    try {
      const response = await apiClient.get('/api/bursars/');
      setBursars(response.data);
    } catch (error) {
      console.error('Error fetching bursars:', error);
    }
  };

  const handleCreateBursar = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Generate password
      const password = Math.random().toString(36).slice(-12);
      const username = formData.email.split('@')[0] + '_bursar';

      const userData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        username: username,
        password: password,
        role: 'bursar',
        phone: formData.phone,
      };

      // Create user
      const userResponse = await apiClient.post('/api/users/', userData);
      
      // Create bursar profile
      await apiClient.post('/api/bursars/', {
        user: userResponse.data.id,
      });

      // Show credentials
      setCredentials({
        email: formData.email,
        username: username,
        password: password,
        role: 'Bursar',
      });
      setShowCredentials(true);

      // Reset form
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
      });
      setShowForm(false);

      // Refresh list
      fetchBursars();
    } catch (error) {
      console.error('Error creating bursar:', error);
      alert('Error creating bursar: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBursar = async (bursarId) => {
    if (!window.confirm('Are you sure you want to delete this bursar?')) return;
    
    try {
      await apiClient.delete(`/api/users/${bursarId}/`);
      fetchBursars();
    } catch (error) {
      console.error('Error deleting bursar:', error);
      alert('Error deleting bursar');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-display font-bold text-slate-900">Bursar Management</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 text-white px-4 py-2 hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Bursar
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <Card className="border-2 border-blue-200">
          <CardContent className="pt-6">
            <form onSubmit={handleCreateBursar} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">First Name</label>
                  <input
                    type="text"
                    required
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="John"
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
                    placeholder="Okafor"
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
                  placeholder="bursar@school.edu"
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
                  Create Bursar
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
                <h3 className="text-lg font-semibold text-green-900"> Bursar Created Successfully!</h3>
                <button onClick={() => setShowCredentials(false)} className="text-green-600 hover:text-green-700"></button>
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
                  alert('Credentials copied to clipboard!');
                }}
                className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                Copy Credentials
              </button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bursars List */}
      <div className="grid gap-4">
        {bursars.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center text-slate-500">
              No bursars created yet. Click "Add Bursar" to get started.
            </CardContent>
          </Card>
        ) : (
          bursars.map((bursar) => (
            <Card key={bursar.id}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      {bursar.user?.first_name} {bursar.user?.last_name}
                    </h3>
                    <p className="text-sm text-slate-600">{bursar.user?.email}</p>
                    {bursar.user?.phone && (
                      <p className="text-sm text-slate-600">{bursar.user.phone}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDeleteBursar(bursar.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};
