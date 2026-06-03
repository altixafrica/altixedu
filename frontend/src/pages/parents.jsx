import React from 'react';
import { Link } from 'react-router-dom';
import { Bell, Download, Eye, MessageSquare, TrendingUp, Users } from 'lucide-react';

import { SiteHeader } from '../components/site-header';
import { SiteFooter } from '../components/site-footer';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

const features = [
  { icon: Eye, title: 'Academic visibility', description: 'View grades, attendance, and school updates without needing separate tools.' },
  { icon: Bell, title: 'Important notices', description: 'Stay close to announcements, reminders, and operational updates from the school.' },
  { icon: MessageSquare, title: 'Direct communication', description: 'Keep teachers and families in a shared loop when attention is needed.' },
  { icon: TrendingUp, title: 'Progress tracking', description: 'Follow student movement over time instead of waiting for the end of term.' },
  { icon: Download, title: 'Practical records', description: 'Access reports and summaries that are easy to share and keep.' },
  { icon: Users, title: 'Family access', description: 'Support households managing more than one learner from a single account.' },
];

export const ParentsPage = () => {
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
              <Badge className="bg-white/10 text-white ring-1 ring-inset ring-white/15">For families and students</Badge>
              <h1 className="mt-5 max-w-4xl text-balance text-4xl font-semibold md:text-6xl">
                A calmer digital link between home and school.
              </h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
                Give parents and students one place for progress, fees, communication, and the daily signals that matter.
              </p>
              <div className="mt-8">
                <Link to="/get-started">
                  <Button size="lg">Create a school workspace</Button>
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
