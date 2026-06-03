import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BookOpen,
  Building2,
  CreditCard,
  GraduationCap,
  ShieldCheck,
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
    body: 'Enrollment, staff, finance, learner risk, and announcements in one operating desk.',
    icon: Building2,
    href: '/school-admins',
  },
  {
    title: 'Teachers',
    body: 'Attendance, scores, class lists, parent messages, and learner follow-up without dashboard noise.',
    icon: GraduationCap,
    href: '/teachers',
  },
  {
    title: 'Families',
    body: 'Parents and students see progress, fees, attendance, results, and school updates clearly.',
    icon: Users,
    href: '/parents',
  },
];

const capabilities = [
  {
    label: 'Academic operations',
    description: 'Classrooms, subjects, attendance, results, and student follow-up.',
    icon: BookOpen,
  },
  {
    label: 'Finance visibility',
    description: 'Fees, balances, receipts, reminders, subscriptions, and collection health.',
    icon: CreditCard,
  },
  {
    label: 'Governance and trust',
    description: 'Role-based access, auditability, ministry reporting, and school oversight.',
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

  return (
    <>
      <SiteHeader />
      <main className="bg-white">
        <section className="relative min-h-[calc(100svh-73px)] overflow-hidden bg-slate-950 text-white">
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{
              backgroundImage: "url('https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?w=1600&h=1000&fit=crop&q=85')",
              backgroundPosition: 'center 35%',
            }}
          />
          <div className="absolute inset-0 bg-slate-950/74" />

          <div className="relative mx-auto flex min-h-[calc(100svh-73px)] max-w-[1440px] items-end px-4 pb-10 pt-16 md:px-6 md:pb-14">
            <div className="max-w-3xl">
              <Badge className="bg-white text-slate-950">Education operations for African schools</Badge>
              <h1 className="mt-5 text-balance text-5xl font-semibold leading-[1.02] text-white md:text-7xl">
                AltixEdu
              </h1>
              <p className="mt-5 max-w-2xl text-xl leading-8 text-slate-100 md:text-2xl">
                A calmer school management system for leaders, teachers, bursars, families, and ministry oversight.
              </p>
              <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
                Bring attendance, results, fees, communication, billing, and reporting into one workflow built for real school operations.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link to="/get-started">
                  <Button size="lg">
                    Create a workspace
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link to="/pricing">
                  <Button size="lg" variant="secondary">Explore pricing</Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="border-b border-slate-200 bg-white py-12">
          <div className="container mx-auto grid gap-4 px-4 md:grid-cols-4 md:px-6">
            {[
              ['Schools running', metrics.schools.toLocaleString()],
              ['Learners managed', metrics.students.toLocaleString()],
              ['Staff accounts', metrics.staff.toLocaleString()],
              ['Countries served', metrics.countries.toLocaleString()],
            ].map(([label, value]) => (
              <div key={label} className="border-l border-slate-200 pl-4">
                <p className="text-sm text-slate-500">{label}</p>
                <p className="mt-2 text-3xl font-semibold text-slate-950">{value}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-white py-16 md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.14em] text-slate-500">The operating desk</p>
                <h2 className="mt-4 max-w-xl text-balance text-3xl font-semibold text-slate-950 md:text-5xl">
                  Less screen stress. More daily control.
                </h2>
                <p className="mt-4 max-w-md text-base leading-7 text-slate-600">
                  AltixEdu is shaped around the jobs schools repeat every day: attendance, results, fees, parent updates, and accountable reporting.
                </p>
              </div>
              <div className="grid gap-4">
                {capabilities.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.label} className="grid gap-4 border-b border-slate-200 pb-6 md:grid-cols-[auto_1fr]">
                      <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-slate-950 text-white">
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

        <section className="border-y border-slate-200 bg-slate-50 py-16 md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.14em] text-slate-500">By role</p>
                <h2 className="mt-3 text-balance text-3xl font-semibold text-slate-950 md:text-5xl">
                  Each person gets the work surface they need.
                </h2>
              </div>
              <Link to="/login">
                <Button variant="outline">Open product</Button>
              </Link>
            </div>

            <div className="grid gap-5 lg:grid-cols-3">
              {audienceCards.map((card) => {
                const Icon = card.icon;
                return (
                  <Link
                    key={card.title}
                    to={card.href}
                    className="group rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition-colors hover:border-slate-300"
                  >
                    <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-slate-950 text-white">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h3 className="mt-6 text-xl font-semibold text-slate-950">{card.title}</h3>
                    <p className="mt-3 text-sm leading-6 text-slate-600">{card.body}</p>
                    <div className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-slate-950">
                      Explore
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        </section>

        <section className="bg-white py-16 md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.14em] text-slate-500">Pricing</p>
                <h2 className="mt-3 text-balance text-3xl font-semibold text-slate-950 md:text-5xl">
                  Plans that match school growth.
                </h2>
                <p className="mt-4 max-w-md text-base leading-7 text-slate-600">
                  Public pricing is connected to the billing catalog, so sales and operations stay aligned.
                </p>
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                {(pricingData?.tiers || []).slice(0, 3).map((tier, index) => (
                  <div
                    key={tier.id || tier.name}
                    className={`rounded-lg border p-5 ${index === 1 ? 'border-slate-950 bg-slate-950 text-white' : 'border-slate-200 bg-slate-50 text-slate-950'}`}
                  >
                    <p className={`text-sm ${index === 1 ? 'text-slate-300' : 'text-slate-500'}`}>
                      {tier.display_name || titleize(tier.name)}
                    </p>
                    <p className="mt-4 text-3xl font-semibold">
                      {formatCurrency(tier.monthly_price || 0, currencyCode)}
                    </p>
                    <p className={`mt-2 text-sm ${index === 1 ? 'text-slate-300' : 'text-slate-600'}`}>
                      Monthly per school
                    </p>
                  </div>
                ))}
                {!pricingData?.tiers?.length ? (
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-slate-600 md:col-span-3">
                    Billing tiers will appear here when the pricing catalog is available.
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </section>

        <section className="bg-slate-950 py-16 text-white md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-center">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.14em] text-slate-500">Ready to launch</p>
                <h2 className="mt-3 max-w-2xl text-balance text-3xl font-semibold md:text-5xl">
                  Move school operations into one clearer rhythm.
                </h2>
                <p className="mt-4 max-w-2xl text-base leading-7 text-slate-400">
                  Start with one campus, one state, or one portfolio. Scale only after the daily work feels simple.
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
