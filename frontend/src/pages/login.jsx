import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { SiteFooter } from '../components/site-footer';
import { SiteHeader } from '../components/site-header';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/form';
import { getDashboardPathForRole, loginUser } from '../lib/django';

export const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await loginUser(email, password);
      navigate(getDashboardPathForRole(response.role));
    } catch (requestError) {
      setError(
        requestError.response?.data?.error ||
          requestError.response?.data?.message ||
          'Login failed. Please check your credentials and try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SiteHeader />
      <main className="min-h-screen bg-gradient-to-b from-white to-slate-50 px-4 py-12">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-slate-900">Welcome back</h1>
            <p className="mt-2 text-slate-600">
              Sign in to continue into your AltixEdu workspace.
            </p>
          </div>

          <Card className="shadow-lg shadow-slate-200/60">
            <CardContent className="pt-6">
              {error ? (
                <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              ) : null}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="login-email" className="mb-2 block text-sm font-medium text-slate-900">
                    Email
                  </label>
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="you@school.com"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    required
                  />
                </div>

                <div>
                  <label htmlFor="login-password" className="mb-2 block text-sm font-medium text-slate-900">
                    Password
                  </label>
                  <Input
                    id="login-password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                  />
                </div>

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Signing in...' : 'Sign in'}
                </Button>
              </form>

              <p className="mt-6 text-center text-sm text-slate-600">
                Need a new workspace?{' '}
                <Link to="/get-started" className="font-medium text-brand-600 hover:text-brand-700">
                  Get started
                </Link>
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
      <SiteFooter />
    </>
  );
};
