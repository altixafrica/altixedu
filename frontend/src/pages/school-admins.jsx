import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart3, Building2, DollarSign, Lock, Settings, Users } from 'lucide-react';

import { SiteHeader } from '../components/site-header';
import { SiteFooter } from '../components/site-footer';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

const features = [
  { icon: Users, title: 'User control', description: 'Provision staff, define access, and keep every role accountable.' },
  { icon: DollarSign, title: 'Financial oversight', description: 'Follow collections, fee status, and payment operations without switching tools.' },
  { icon: BarChart3, title: 'Decision visibility', description: 'See performance, attendance, and operational movement in one place.' },
  { icon: Building2, title: 'School setup', description: 'Manage identity, brand settings, and institutional structure with confidence.' },
  { icon: Settings, title: 'Bulk workflows', description: 'Import, update, and organize records at the pace real schools require.' },
  { icon: Lock, title: 'Policy and trust', description: 'Support auditability, permissions, and tighter operational governance.' },
];

export const SchoolAdminsPage = () => {
  return (
    <>
      <SiteHeader />
      <main className="bg-white">
        <section className="relative border-b border-slate-200 py-16 text-white md:py-20 overflow-hidden">
          {/* Background Image Layer */}
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{
              backgroundImage: "url('https://images.unsplash.com/photo-1552664730-d307ca884978?w=1440&h=900&fit=crop&q=80')",
              backgroundAttachment: "fixed",
              backgroundPosition: "center 20%",
            }}
          />

          {/* Dark Overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-950/85 via-slate-900/80 to-slate-950/85" />

          {/* Content */}
          <div className="relative z-10">
            <div className="container mx-auto px-4 md:px-6">
              <Badge className="bg-white/10 text-white ring-1 ring-inset ring-white/15">For school leaders</Badge>
              <h1 className="mt-5 max-w-4xl text-balance text-4xl font-semibold md:text-6xl">
                One operating surface for the people running the institution.
              </h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
                AltixEdu gives administrators one clear workspace for finance, staff, reporting, setup, and day-to-day school control.
              </p>
              <div className="mt-8">
                <Link to="/get-started">
                  <Button size="lg">Launch your school workspace</Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <div key={feature.title} className="rounded-[28px] border border-slate-200 bg-slate-50 p-6">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-slate-950 shadow-sm">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h2 className="mt-8 text-2xl font-semibold text-slate-950">{feature.title}</h2>
                    <p className="mt-3 text-sm leading-6 text-slate-600">{feature.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
};
