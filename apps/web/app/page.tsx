'use client'

import Link from 'next/link'
import { Navbar } from '@/components/layout/navbar'
import { Footer } from '@/components/layout/footer'

export default function Home() {
  return (
    <main className="min-h-screen bg-stone-50/50">
      <Navbar />

      {/* Hero */}
      <section className="pt-24 sm:pt-36 pb-20 sm:pb-28 px-4 sm:px-6">
        <div className="max-w-3xl mx-auto text-center animate-fade-in">
          <h1 className="text-4xl sm:text-5xl font-semibold text-stone-900 leading-[1.15] tracking-tight mb-6">
            Your growth story,
            <br />
            <span className="text-stone-400">told through interviews.</span>
          </h1>
          <p className="text-lg text-stone-500 leading-relaxed mb-12 max-w-xl mx-auto">
            Most platforms show a snapshot. Pathway shows your trajectory.
            Interview monthly, connect your GitHub, and let employers see
            how far you've come.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              href="/register"
              className="inline-flex items-center justify-center px-8 py-3.5 text-sm font-medium text-white bg-stone-900 rounded-full hover:bg-stone-800 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg"
            >
              Get Started Free
            </Link>
            <Link
              href="/employer"
              className="inline-flex items-center justify-center px-8 py-3.5 text-sm font-medium text-stone-500 hover:text-stone-900 transition-colors duration-300"
            >
              I'm hiring <svg className="inline w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" /></svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Problem/Solution */}
      <section className="py-16 sm:py-28 px-4 sm:px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-10 md:gap-24">
            <div className="animate-slide-up" style={{ animationDelay: '100ms' }}>
              <p className="text-[11px] font-medium text-stone-400 uppercase tracking-[0.2em] mb-4">The problem</p>
              <h2 className="text-xl font-semibold text-stone-900 mb-4 leading-snug">
                Traditional hiring is broken for students
              </h2>
              <p className="text-stone-500 leading-relaxed">
                One interview, one chance. Employers only see where you are today,
                not the progress you've made. Your sophomore self doesn't reflect
                your senior capabilities.
              </p>
            </div>
            <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
              <p className="text-[11px] font-medium text-teal-600/70 uppercase tracking-[0.2em] mb-4">Our approach</p>
              <h2 className="text-xl font-semibold text-stone-900 mb-4 leading-snug">
                Growth over snapshots
              </h2>
              <p className="text-stone-500 leading-relaxed">
                Interview monthly throughout college. Each interview builds on the last.
                Employers see your improvement curve—how you learn, adapt, and grow
                over 2-4 years.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 sm:py-32 px-4 sm:px-6 bg-stone-900 text-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-20">
            <p className="text-[11px] font-medium text-stone-500 uppercase tracking-[0.2em] mb-4">Features</p>
            <h2 className="text-2xl font-semibold mb-4">
              Built for how students actually grow
            </h2>
            <p className="text-stone-400">
              Not just another job board. A career development platform.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-x-12 md:gap-y-14">
            {[
              {
                title: 'Progress tracking',
                description: 'See your scores improve month over month. Understand your strengths and areas to develop.',
              },
              {
                title: 'GitHub integration',
                description: 'Your projects and contributions speak for themselves. We surface your best work automatically.',
              },
              {
                title: 'Multiple attempts',
                description: 'Bad interview day? Interview again next month. Your best score is what employers see.',
              },
              {
                title: 'Role-specific questions',
                description: 'Tailored interviews for engineering, data, business, and design roles.',
              },
              {
                title: 'AI-powered analysis',
                description: 'Each interview is analyzed by AI across 5 dimensions. Employers see your growth over time.',
              },
              {
                title: 'Employer matching',
                description: 'Companies find you based on your vertical, scores, and growth trajectory.',
              },
            ].map((feature, i) => (
              <div
                key={feature.title}
                className="animate-fade-in group"
                style={{ animationDelay: `${i * 50}ms` }}
              >
                <h3 className="font-medium text-white mb-2.5 group-hover:text-teal-200 transition-colors duration-300">{feature.title}</h3>
                <p className="text-sm text-stone-400 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Career paths */}
      <section className="py-20 sm:py-32 px-4 sm:px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-[11px] font-medium text-stone-400 uppercase tracking-[0.2em] mb-4">Verticals</p>
            <h2 className="text-2xl font-semibold text-stone-900 mb-4">
              Four career paths
            </h2>
            <p className="text-stone-500">
              One interview per vertical. Your profile reaches all employers in that space.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-5">
            {[
              { name: 'Engineering', roles: 'Software, Frontend, Backend, Mobile, DevOps' },
              { name: 'Data', roles: 'Analytics, Data Science, ML, Data Engineering' },
              { name: 'Business', roles: 'Product, Marketing, Finance, Consulting' },
              { name: 'Design', roles: 'UX, UI, Product Design' },
            ].map((vertical, i) => (
              <div
                key={vertical.name}
                className="p-6 bg-stone-50 rounded-2xl hover:bg-stone-100 transition-all duration-300 hover:scale-[1.02] animate-slide-up cursor-default"
                style={{ animationDelay: `${i * 75}ms` }}
              >
                <h3 className="font-medium text-stone-900 mb-2">{vertical.name}</h3>
                <p className="text-xs text-stone-500 leading-relaxed">{vertical.roles}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social proof */}
      <section className="py-28 px-6 bg-stone-50/50">
        <div className="max-w-2xl mx-auto text-center">
          <p className="text-xl text-stone-600 leading-relaxed font-light mb-8">
            "Finally, a platform that understands college students aren't finished products.
            Pathway let me show my growth from a nervous sophomore to a confident senior."
          </p>
          <p className="text-sm text-stone-400">— CS Student, Stanford '25</p>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 sm:py-32 px-4 sm:px-6 bg-white">
        <div className="max-w-xl mx-auto text-center">
          <h2 className="text-2xl font-semibold text-stone-900 mb-4">
            Start building your trajectory
          </h2>
          <p className="text-stone-500 mb-10">
            Free for students. Your first interview takes 15 minutes.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center justify-center px-10 py-4 text-sm font-medium text-white bg-stone-900 rounded-full hover:bg-stone-800 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl"
          >
            Create Free Account
          </Link>
          <p className="mt-8 text-xs text-stone-400">
            No credit card required. Interview from anywhere.
          </p>
        </div>
      </section>

      <Footer />
    </main>
  )
}
