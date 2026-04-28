import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertCircle,
  ArrowRight,
  Check,
  Eye,
  EyeOff,
  Loader2,
  Shield,
} from 'lucide-react';

import { SiteFooter } from '../components/site-footer';
import { SiteHeader } from '../components/site-header';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Input, Select } from '../components/ui/form';
import { checkSubdomain, registerSchool } from '../lib/django';

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const countries = [
  { value: 'Nigeria', label: 'Nigeria' },
  { value: 'Kenya', label: 'Kenya' },
  { value: 'Ghana', label: 'Ghana' },
  { value: 'Uganda', label: 'Uganda' },
  { value: 'Tanzania', label: 'Tanzania' },
];

export const GetStartedPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [checkingSubdomain, setCheckingSubdomain] = useState(false);
  const [subdomainStatus, setSubdomainStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    school_name: '',
    school_email: '',
    city: '',
    state: '',
    country: 'Nigeria',
    subdomain: '',
    admin_first_name: '',
    admin_last_name: '',
    admin_email: '',
    phone: '',
    admin_password: '',
    confirm_password: '',
  });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));

    if (name === 'subdomain') {
      setSubdomainStatus('');
    }
  };

  const handleCheckSubdomain = async () => {
    if (!formData.subdomain) return;

    setCheckingSubdomain(true);
    setSubdomainStatus('');
    setError('');

    try {
      const result = await checkSubdomain(formData.subdomain, formData.school_name);
      setSubdomainStatus(result.is_available ? 'available' : 'taken');
    } catch (requestError) {
      setSubdomainStatus('error');
      setError(
        requestError.response?.data?.error ||
          'We could not verify the subdomain right now.'
      );
    } finally {
      setCheckingSubdomain(false);
    }
  };

  const isStepOneValid =
    formData.school_name.trim().length >= 2 &&
    emailPattern.test(formData.school_email) &&
    formData.city.trim().length >= 2 &&
    formData.country &&
    formData.subdomain.trim().length >= 3 &&
    subdomainStatus === 'available';

  const isStepTwoValid =
    formData.admin_first_name.trim().length >= 2 &&
    formData.admin_last_name.trim().length >= 2 &&
    emailPattern.test(formData.admin_email) &&
    formData.admin_password.length >= 8 &&
    formData.admin_password === formData.confirm_password;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await registerSchool(formData);
      setSuccess(response.message || 'School registered successfully.');
      setTimeout(() => navigate('/login'), 1800);
    } catch (requestError) {
      const responseError = requestError.response?.data;
      const firstError =
        typeof responseError === 'string'
          ? responseError
          : responseError?.error ||
            responseError?.message ||
            Object.values(responseError || {})[0]?.[0];

      setError(firstError || 'Registration failed. Please review your details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SiteHeader />
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12">
        <div className="container mx-auto max-w-6xl px-4 md:px-6">
          <div className="mb-10 text-center">
            <Badge variant="primary">School onboarding</Badge>
            <h1 className="mt-4 text-4xl font-bold text-white md:text-5xl">
              Create your AltixEdu workspace
            </h1>
            <p className="mt-3 text-lg text-slate-300">
              Launch a school environment with the core structure, admin access, and billing seed already in place.
            </p>
          </div>

          <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
            <div className="space-y-5">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <div className="flex items-center gap-3">
                  <Shield className="h-5 w-5 text-green-400" />
                  <p className="font-medium text-white">Provisioning in one flow</p>
                </div>
                <p className="mt-3 text-sm text-slate-300">
                  Create the school record, admin account, subscription seed, and login-ready workspace in one submission.
                </p>
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <p className="text-sm uppercase tracking-[0.24em] text-slate-400">
                  Progress
                </p>
                <div className="mt-4 flex gap-2">
                  {[1, 2].map((item) => (
                    <div
                      key={item}
                      className={`h-2 flex-1 rounded-full ${
                        item <= step ? 'bg-brand-500' : 'bg-slate-700'
                      }`}
                    />
                  ))}
                </div>
                <p className="mt-3 text-sm text-slate-300">
                  Step {step} of 2: {step === 1 ? 'School details' : 'Admin account'}
                </p>
              </div>
            </div>

            <Card className="border-slate-700 bg-slate-900/60 shadow-2xl shadow-black/20">
              <CardContent className="pt-6">
                {error ? (
                  <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                    <AlertCircle className="mt-0.5 h-5 w-5" />
                    <span>{error}</span>
                  </div>
                ) : null}

                {success ? (
                  <div className="mb-6 flex items-start gap-3 rounded-xl border border-green-500/40 bg-green-500/10 px-4 py-3 text-sm text-green-200">
                    <Check className="mt-0.5 h-5 w-5" />
                    <span>{success}</span>
                  </div>
                ) : null}

                <form onSubmit={handleSubmit} className="space-y-5">
                  {step === 1 ? (
                    <>
                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="md:col-span-2">
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            School name
                          </label>
                          <Input
                            name="school_name"
                            value={formData.school_name}
                            onChange={handleChange}
                            placeholder="Sunrise Academy"
                            className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>

                        <div>
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            School email
                          </label>
                          <Input
                            name="school_email"
                            type="email"
                            value={formData.school_email}
                            onChange={handleChange}
                            placeholder="info@sunrise.edu"
                            className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>

                        <div>
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            City
                          </label>
                          <Input
                            name="city"
                            value={formData.city}
                            onChange={handleChange}
                            placeholder="Lagos"
                            className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>

                        <div>
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            State or province
                          </label>
                          <Input
                            name="state"
                            value={formData.state}
                            onChange={handleChange}
                            placeholder="Optional"
                            className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                          />
                        </div>

                        <div>
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            Country
                          </label>
                          <Select
                            name="country"
                            value={formData.country}
                            onChange={handleChange}
                            className="border-slate-600 bg-slate-950 text-white"
                          >
                            {countries.map((country) => (
                              <option key={country.value} value={country.value}>
                                {country.label}
                              </option>
                            ))}
                          </Select>
                        </div>

                        <div className="md:col-span-2">
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            School subdomain
                          </label>
                          <div className="flex gap-3">
                            <Input
                              name="subdomain"
                              value={formData.subdomain}
                              onChange={handleChange}
                              placeholder="sunrise-academy"
                              className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                              required
                            />
                            <Button
                              type="button"
                              variant="secondary"
                              onClick={handleCheckSubdomain}
                              disabled={checkingSubdomain || !formData.subdomain}
                            >
                              {checkingSubdomain ? (
                                <>
                                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                  Checking
                                </>
                              ) : (
                                'Check'
                              )}
                            </Button>
                          </div>
                          <div className="mt-3 text-sm">
                            {subdomainStatus === 'available' ? (
                              <span className="text-green-400">This subdomain is available.</span>
                            ) : null}
                            {subdomainStatus === 'taken' ? (
                              <span className="text-red-400">This subdomain is already taken.</span>
                            ) : null}
                            {subdomainStatus === 'error' ? (
                              <span className="text-amber-400">Subdomain check failed. Try again.</span>
                            ) : null}
                          </div>
                        </div>
                      </div>

                      <Button
                        type="button"
                        className="w-full"
                        disabled={!isStepOneValid}
                        onClick={() => setStep(2)}
                      >
                        Continue to admin setup
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </>
                  ) : (
                    <>
                      <div className="grid gap-4 md:grid-cols-2">
                        <div>
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            Admin first name
                          </label>
                          <Input
                            name="admin_first_name"
                            value={formData.admin_first_name}
                            onChange={handleChange}
                            placeholder="Ada"
                            className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>

                        <div>
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            Admin last name
                          </label>
                          <Input
                            name="admin_last_name"
                            value={formData.admin_last_name}
                            onChange={handleChange}
                            placeholder="Nwosu"
                            className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>

                        <div>
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            Admin email
                          </label>
                          <Input
                            name="admin_email"
                            type="email"
                            value={formData.admin_email}
                            onChange={handleChange}
                            placeholder="admin@sunrise.edu"
                            className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>

                        <div>
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            Phone number
                          </label>
                          <Input
                            name="phone"
                            value={formData.phone}
                            onChange={handleChange}
                            placeholder="+234 800 000 0000"
                            className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                          />
                        </div>

                        <div className="md:col-span-2">
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            Admin password
                          </label>
                          <div className="relative">
                            <Input
                              name="admin_password"
                              type={showPassword ? 'text' : 'password'}
                              value={formData.admin_password}
                              onChange={handleChange}
                              placeholder="Minimum 8 characters"
                              className="border-slate-600 bg-slate-950 pr-12 text-white placeholder:text-slate-500"
                              required
                            />
                            <button
                              type="button"
                              className="absolute right-3 top-3 text-slate-400"
                              onClick={() => setShowPassword((current) => !current)}
                            >
                              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                          </div>
                        </div>

                        <div className="md:col-span-2">
                          <label className="mb-2 block text-sm font-medium text-slate-200">
                            Confirm password
                          </label>
                          <Input
                            name="confirm_password"
                            type={showPassword ? 'text' : 'password'}
                            value={formData.confirm_password}
                            onChange={handleChange}
                            placeholder="Repeat the password"
                            className="border-slate-600 bg-slate-950 text-white placeholder:text-slate-500"
                            required
                          />
                        </div>
                      </div>

                      <div className="flex gap-3">
                        <Button type="button" variant="secondary" className="flex-1" onClick={() => setStep(1)}>
                          Back
                        </Button>
                        <Button type="submit" className="flex-1" disabled={loading || !isStepTwoValid}>
                          {loading ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Creating workspace...
                            </>
                          ) : (
                            'Create school workspace'
                          )}
                        </Button>
                      </div>
                    </>
                  )}
                </form>

                <p className="mt-6 text-center text-sm text-slate-400">
                  Already have an account?{' '}
                  <Link to="/login" className="font-medium text-brand-400 hover:text-brand-300">
                    Sign in
                  </Link>
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
      <SiteFooter />
    </>
  );
};
