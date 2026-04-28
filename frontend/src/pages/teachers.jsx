import React from 'react';
import { Link } from 'react-router-dom';
import { BarChart3, BookMarked, CheckCircle2, Clock, MessageSquare, User } from 'lucide-react';

import { SiteHeader } from '../components/site-header';
import { SiteFooter } from '../components/site-footer';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

const features = [
  { icon: Clock, title: 'Attendance flow', description: 'Mark attendance quickly and surface patterns before they become bigger issues.' },
  { icon: BookMarked, title: 'Assessment tracking', description: 'Capture scores, manage subjects, and keep academic records visible.' },
  { icon: MessageSquare, title: 'Communication', description: 'Stay connected with families and students without leaving the classroom workflow.' },
  { icon: BarChart3, title: 'Student signals', description: 'Use alerts and summaries to spot learners who need extra attention.' },
  { icon: CheckCircle2, title: 'Classroom focus', description: 'Keep your daily work organized around classes, students, and follow-up tasks.' },
  { icon: User, title: 'Professional control', description: 'See the work that matters to your role without administrative clutter.' },
];

export const TeachersPage = () => {
  return (
    <>
      <SiteHeader />
      <main className="bg-white">
        <section className="border-b border-slate-200 bg-slate-950 py-16 text-white md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <Badge className="bg-white/10 text-white ring-1 ring-inset ring-white/15">For teachers</Badge>
            <h1 className="mt-5 max-w-4xl text-balance text-4xl font-semibold md:text-6xl">
              A classroom workspace designed to reduce admin drag.
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
              AltixEdu helps teachers move through attendance, grading, communication, and student follow-up with more clarity and less friction.
            </p>
            <div className="mt-8">
              <Link to="/get-started">
                <Button size="lg">Start your school setup</Button>
              </Link>
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
