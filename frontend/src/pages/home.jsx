import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BadgeCheck,
  BookOpen,
  Building2,
  CreditCard,
  Globe2,
  GraduationCap,
  ShieldCheck,
  Sparkles,
  Users,
} from 'lucide-react';

import { SiteFooter } from '../components/site-footer';
import { SiteHeader } from '../components/site-header';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { getPlatformOverview, getPublicPricing } from '../lib/django';
import { formatCurrency, titleize } from '../lib/format';

const audienceCards = [
  {
    title: 'School leaders',
    body: 'Operate enrollment, staff, finance, and compliance from one clear control surface.',
    icon: Building2,
    href: '/school-admins',
  },
  {
    title: 'Teachers',
    body: 'Track attendance, follow student risk, and keep classroom actions moving without friction.',
    icon: GraduationCap,
    href: '/teachers',
  },
  {
    title: 'Families',
    body: 'Give parents and students one calm place for progress, fees, updates, and communication.',
    icon: Users,
    href: '/parents',
  },
];

const operatingSystemItems = [
  {
    label: 'Academic operations',
    description: 'Classrooms, attendance, results, and student follow-up in one workflow.',
    icon: BookOpen,
  },
  {
    label: 'Finance visibility',
    description: 'Track fees, balances, collections, subscriptions, and school-level payment health.',
    icon: CreditCard,
  },
  {
    label: 'Governance and trust',
    description: 'Role-based access, auditability, and ministry-level reporting for growing systems.',
    icon: ShieldCheck,
  },
];

const statValue = (value, fallback) => (value === null || value === undefined ? fallback : value);

export const HomePage = () => {
  const [platformData, setPlatformData] = useState(null);
  const [pricingData, setPricingData] = useState(null);

  useEffect(() => {
    const load = async () => {
      const [platform, pricing] = await Promise.all([
        getPlatformOverview(),
        getPublicPricing(),
      ]);

      setPlatformData(platform);
      setPricingData(pricing);
    };

    load();
  }, []);

  const metrics = useMemo(
    () => ({
      schools: statValue(platformData?.metrics?.active_schools, 250),
      staff: statValue(platformData?.metrics?.staff_accounts, 15000),
      students: statValue(platformData?.metrics?.students_managed, 125000),
      countries: statValue(platformData?.metrics?.countries, 5),
    }),
    [platformData]
  );

  const currencyCode = pricingData?.currency || 'NGN';
  const featuredTier = pricingData?.tiers?.[1] || pricingData?.tiers?.[0];

  return (
    <>
      <SiteHeader />
      <main className="bg-white">
        <section className="relative overflow-hidden bg-slate-950 text-white">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.22),transparent_32%),radial-gradient(circle_at_80%_20%,rgba(16,185,129,0.12),transparent_24%),linear-gradient(180deg,rgba(15,23,42,0.88),rgba(2,6,23,1))]" />
          <div className="absolute inset-0 bg-grid opacity-20" />
          <div className="relative mx-auto flex min-h-[calc(100svh-73px)] max-w-[1440px] items-end px-4 pb-10 pt-10 md:px-6 md:pb-14 md:pt-12">
            <div className="grid w-full gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-end">
              <div className="max-w-3xl">
                <Badge className="bg-white/10 text-white ring-1 ring-inset ring-white/15">
                  Education operations at system scale
                </Badge>
                <h1 className="mt-6 max-w-3xl text-balance text-5xl font-semibold leading-[1.02] text-white md:text-7xl">
                  AltixEdu
                </h1>
                <p className="mt-5 max-w-2xl text-balance text-xl leading-8 text-slate-300 md:text-2xl">
                  A premium operating layer for schools, educators, families, and government oversight.
                </p>
                <p className="mt-6 max-w-2xl text-base leading-7 text-slate-400 md:text-lg">
                  Bring academics, attendance, billing, communication, and role-based workflows into one product that feels modern, accountable, and ready for scale.
                </p>
                <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                  <Link to="/get-started">
                    <Button size="lg">
                      Create a workspace
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                  <Link to="/pricing">
                    <Button size="lg" variant="secondary">
                      Explore pricing
                    </Button>
                  </Link>
                </div>
                <div className="mt-10 grid gap-6 border-t border-white/10 pt-6 sm:grid-cols-3">
                  <div>
                    <p className="text-sm text-slate-400">Schools running</p>
                    <p className="mt-2 text-3xl font-semibold text-white">{metrics.schools.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Learners managed</p>
                    <p className="mt-2 text-3xl font-semibold text-white">{metrics.students.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Countries served</p>
                    <p className="mt-2 text-3xl font-semibold text-white">{metrics.countries.toLocaleString()}</p>
                  </div>
                </div>
              </div>

              <div className="lg:pb-4">
                <div className="overflow-hidden rounded-[32px] border border-white/10 bg-white/6 p-4 shadow-2xl shadow-black/20 backdrop-blur-xl">
                  <div className="rounded-[28px] bg-slate-900/90 p-5">
                    <div className="flex items-center justify-between border-b border-white/10 pb-4">
                      <div>
                        <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Operating snapshot</p>
                        <p className="mt-2 text-lg font-medium text-white">Executive workspace</p>
                      </div>
                      <div className="inline-flex items-center gap-2 rounded-full bg-emerald-500/12 px-3 py-1 text-xs font-medium text-emerald-300">
                        <Sparkles className="h-3.5 w-3.5" />
                        Live system
                      </div>
                    </div>

                    <div className="mt-5 grid gap-4 md:grid-cols-2">
                      <div className="rounded-3xl bg-white px-5 py-6 text-slate-950">
                        <p className="text-sm text-slate-500">Monthly collections</p>
                        <p className="mt-3 text-3xl font-semibold">{formatCurrency(28400000, currencyCode)}</p>
                        <p className="mt-5 text-sm text-slate-600">Collections, balances, and fee risk visible by school and portfolio.</p>
                      </div>
                      <div className="space-y-4">
                        <div className="rounded-3xl bg-slate-800 px-5 py-5">
                          <p className="text-sm text-slate-400">Staff accounts</p>
                          <p className="mt-2 text-2xl font-semibold text-white">{metrics.staff.toLocaleString()}</p>
                        </div>
                        <div className="rounded-3xl bg-slate-800 px-5 py-5">
                          <p className="text-sm text-slate-400">Featured tier</p>
                          <p className="mt-2 text-xl font-semibold text-white">
                            {featuredTier?.display_name || 'Professional Plan'}
                          </p>
                          <p className="mt-2 text-sm text-slate-400">
                            {featuredTier?.monthly_price
                              ? `${formatCurrency(featuredTier.monthly_price, currencyCode)} monthly`
                              : 'Configured from the billing catalog'}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-3">
                      {['Role-based access', 'Parent visibility', 'State reporting'].map((item) => (
                        <div key={item} className="rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 text-sm text-slate-300">
                          {item}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="border-b border-slate-200 bg-white py-16 md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.18em] text-slate-500">Why teams choose AltixEdu</p>
                <h2 className="mt-4 max-w-xl text-balance text-3xl font-semibold text-slate-950 md:text-5xl">
                  Built like a real operating system, not a patchwork of screens.
                </h2>
              </div>
              <div className="grid gap-4">
                {operatingSystemItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.label} className="grid gap-4 rounded-[28px] border border-slate-200 bg-slate-50 p-6 md:grid-cols-[auto_1fr] md:items-start">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-slate-950 shadow-sm">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-slate-950">{item.label}</h3>
                        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">{item.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        <section className="bg-slate-50 py-16 md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.18em] text-slate-500">Experiences by role</p>
                <h2 className="mt-3 text-balance text-3xl font-semibold text-slate-950 md:text-5xl">
                  One platform, tuned for every operator in the system.
                </h2>
              </div>
              <Link to="/login">
                <Button variant="outline">Open the product</Button>
              </Link>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
              {audienceCards.map((card) => {
                const Icon = card.icon;
                return (
                  <Link
                    key={card.title}
                    to={card.href}
                    className="group rounded-[30px] border border-slate-200 bg-white p-7 shadow-sm transition-transform hover:-translate-y-1"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-white">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h3 className="mt-8 text-2xl font-semibold text-slate-950">{card.title}</h3>
                    <p className="mt-3 text-sm leading-6 text-slate-600">{card.body}</p>
                    <div className="mt-8 inline-flex items-center gap-2 text-sm font-medium text-slate-950">
                      Explore
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        </section>

        <section className="border-y border-slate-200 bg-white py-16 md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.18em] text-slate-500">Commercial clarity</p>
                <h2 className="mt-3 text-balance text-3xl font-semibold text-slate-950 md:text-5xl">
                  Pricing that aligns with school growth.
                </h2>
                <p className="mt-4 max-w-md text-base leading-7 text-slate-600">
                  The billing catalog is already wired into the product, so your public pricing and your operational subscriptions stay in step.
                </p>
              </div>

              <div className="rounded-[32px] border border-slate-200 bg-slate-950 p-6 text-white">
                {pricingData?.tiers?.length ? (
                  <div className="grid gap-4 md:grid-cols-3">
                    {pricingData.tiers.slice(0, 3).map((tier, index) => (
                      <div
                        key={tier.id || tier.name}
                        className={`rounded-[24px] p-5 ${index === 1 ? 'bg-white text-slate-950' : 'bg-white/6 text-white'}`}
                      >
                        <p className={`text-sm ${index === 1 ? 'text-slate-500' : 'text-slate-400'}`}>
                          {tier.display_name || titleize(tier.name)}
                        </p>
                        <p className="mt-4 text-3xl font-semibold">
                          {formatCurrency(tier.monthly_price || 0, currencyCode)}
                        </p>
                        <p className={`mt-2 text-sm ${index === 1 ? 'text-slate-600' : 'text-slate-400'}`}>
                          Monthly per school workspace
                        </p>
                        <div className={`mt-6 text-sm leading-6 ${index === 1 ? 'text-slate-600' : 'text-slate-300'}`}>
                          {(tier.features || []).slice(0, 3).map((feature) => (
                            <div key={feature} className="flex items-start gap-2">
                              <BadgeCheck className="mt-0.5 h-4 w-4" />
                              <span>{titleize(feature.replaceAll('_', ' '))}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="rounded-[24px] bg-white/6 p-6 text-slate-300">
                    Billing tiers will appear here when the pricing catalog is available.
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        <section className="bg-slate-950 py-16 text-white md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.18em] text-slate-500">Ready to launch</p>
                <h2 className="mt-3 max-w-2xl text-balance text-3xl font-semibold md:text-5xl">
                  Move your school into a clearer, faster, more accountable operating rhythm.
                </h2>
                <p className="mt-4 max-w-2xl text-base leading-7 text-slate-400">
                  Start with one campus, one state, or one portfolio. AltixEdu is built to scale with the institutions it serves.
                </p>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row lg:flex-col">
                <Link to="/get-started">
                  <Button size="lg">Create a workspace</Button>
                </Link>
                <Link to="/login">
                  <Button size="lg" variant="secondary">Sign in</Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
};
