import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, ShieldCheck } from 'lucide-react';

import { SiteFooter } from '../components/site-footer';
import { SiteHeader } from '../components/site-header';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { getPublicPricing } from '../lib/django';
import { formatCurrency, titleize } from '../lib/format';

export const PricingPage = () => {
  const [pricingData, setPricingData] = useState(null);

  useEffect(() => {
    const loadPricing = async () => {
      const result = await getPublicPricing();
      setPricingData(result);
    };

    loadPricing();
  }, []);

  const currencyCode = pricingData?.currency || 'NGN';
  const tiers = pricingData?.tiers || [];

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
              <Badge className="bg-white/10 text-white ring-1 ring-inset ring-white/15">
                Transparent pricing
              </Badge>
              <h1 className="mt-5 max-w-4xl text-balance text-4xl font-semibold md:text-6xl">
                Plans designed for growing schools and coordinated education systems.
              </h1>
              <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
                Choose the operating layer that fits your current scale, then expand without rebuilding your workflows.
              </p>
            </div>
          </div>
        </section>

        <section className="py-16 md:py-20">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-3">
              {tiers.length ? (
                tiers.map((tier, index) => (
                  <div
                    key={tier.id || tier.name}
                    className={`rounded-[30px] border p-7 ${
                      index === 1
                        ? 'border-slate-950 bg-slate-950 text-white shadow-xl shadow-slate-950/10'
                        : 'border-slate-200 bg-slate-50 text-slate-950'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={`text-sm ${index === 1 ? 'text-slate-300' : 'text-slate-500'}`}>
                          {tier.display_name || titleize(tier.name)}
                        </p>
                        <h2 className="mt-3 text-3xl font-semibold">
                          {formatCurrency(tier.monthly_price || 0, currencyCode)}
                        </h2>
                      </div>
                      {index === 1 ? <Badge className="bg-white text-slate-950">Recommended</Badge> : null}
                    </div>

                    <p className={`mt-4 text-sm leading-6 ${index === 1 ? 'text-slate-300' : 'text-slate-600'}`}>
                      {titleize((tier.support_level || 'standard').replaceAll('_', ' '))} support, with annual pricing at{' '}
                      {tier.annual_price ? formatCurrency(tier.annual_price, currencyCode) : 'custom'}.
                    </p>

                    <div className={`mt-8 grid gap-3 rounded-[24px] p-5 ${index === 1 ? 'bg-white/6' : 'bg-white'}`}>
                      <div className="flex items-center justify-between text-sm">
                        <span>Students</span>
                        <span className="font-medium">{tier.max_students}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Teachers</span>
                        <span className="font-medium">{tier.max_teachers}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Trial period</span>
                        <span className="font-medium">{tier.trial_days} days</span>
                      </div>
                    </div>

                    <div className={`mt-8 space-y-3 text-sm ${index === 1 ? 'text-slate-200' : 'text-slate-700'}`}>
                      {(tier.features || []).map((feature) => (
                        <div key={feature} className="flex items-start gap-3">
                          <Check className="mt-0.5 h-4 w-4 flex-none" />
                          <span>{titleize(feature.replaceAll('_', ' '))}</span>
                        </div>
                      ))}
                    </div>

                    <Link to="/get-started" className="mt-8 block">
                      <Button fullWidth variant={index === 1 ? 'secondary' : 'primary'}>
                        Start with this plan
                      </Button>
                    </Link>
                  </div>
                ))
              ) : (
                <div className="rounded-[28px] border border-slate-200 bg-slate-50 p-8 text-slate-600 lg:col-span-3">
                  Pricing tiers will appear here once the billing catalog is available.
                </div>
              )}
            </div>

            {pricingData?.government_bulk_pricing?.length ? (
              <div className="mt-12 rounded-[30px] border border-slate-200 bg-slate-950 p-8 text-white">
                <div className="flex items-center gap-3">
                  <ShieldCheck className="h-5 w-5" />
                  <h2 className="text-2xl font-semibold">Government and multi-school pricing</h2>
                </div>
                <div className="mt-6 grid gap-4 md:grid-cols-4">
                  {pricingData.government_bulk_pricing.map((band) => (
                    <div key={band.min_schools} className="rounded-[22px] bg-white/6 p-5">
                      <p className="text-sm text-slate-400">{band.min_schools}+ schools</p>
                      <p className="mt-2 text-3xl font-semibold">{band.discount_percentage}%</p>
                      <p className="mt-2 text-sm text-slate-300">volume discount</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
};
