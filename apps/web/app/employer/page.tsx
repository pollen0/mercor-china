'use client'

import Link from 'next/link'
import { Navbar } from '@/components/layout/navbar'
import { Footer } from '@/components/layout/footer'

export default function EmployerLandingPage() {
  return (
    <main className="min-h-screen bg-stone-50/50">
      <Navbar />

      {/* Hero */}
      <section className="pt-36 pb-28 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-[11px] font-medium text-teal-600/70 uppercase tracking-[0.2em] mb-6">For Employers</p>
          <h1 className="text-4xl sm:text-5xl font-semibold text-stone-900 leading-[1.15] tracking-tight mb-6">
            Hire based on trajectory,
            <br />
            <span className="text-stone-400">not just a single snapshot.</span>
          </h1>
          <p className="text-lg text-stone-500 leading-relaxed mb-12 max-w-xl mx-auto">
            See how candidates grow over months of AI-assessed interviews,
            GitHub contributions, and real project work. Stop guessing —
            watch the trajectory.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              href="/employer/login"
              className="inline-flex items-center justify-center px-8 py-3.5 text-sm font-medium text-white bg-stone-900 rounded-full hover:bg-stone-800 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg"
            >
              Start Browsing Talent
            </Link>
            <Link
              href="#how-it-works"
              className="inline-flex items-center justify-center px-8 py-3.5 text-sm font-medium text-stone-500 hover:text-stone-900 transition-colors duration-300"
            >
              See how it works
            </Link>
          </div>
        </div>
      </section>

      {/* Problem/Solution */}
      <section className="py-28 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-16 md:gap-24">
            <div>
              <p className="text-[11px] font-medium text-stone-400 uppercase tracking-[0.2em] mb-4">The problem</p>
              <h2 className="text-xl font-semibold text-stone-900 mb-4 leading-snug">
                Resumes and one-off interviews don't work
              </h2>
              <p className="text-stone-500 leading-relaxed">
                You're hiring entry-level engineers, PMs, and analysts.
                Every candidate looks the same on paper. One interview can't
                tell you who will grow fastest on the job.
              </p>
            </div>
            <div>
              <p className="text-[11px] font-medium text-teal-600/70 uppercase tracking-[0.2em] mb-4">Our approach</p>
              <h2 className="text-xl font-semibold text-stone-900 mb-4 leading-snug">
                Months of signal, not a single data point
              </h2>
              <p className="text-stone-500 leading-relaxed">
                Students interview monthly on Pathway. You see their improvement curve,
                GitHub authenticity analysis, coding session reviews, and transcript data.
                Hire the ones who learn fastest.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* What you see */}
      <section id="how-it-works" className="py-32 px-6 bg-stone-900 text-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-20">
            <p className="text-[11px] font-medium text-stone-500 uppercase tracking-[0.2em] mb-4">What you get</p>
            <h2 className="text-2xl font-semibold mb-4">
              Every signal that matters, in one place
            </h2>
            <p className="text-stone-400">
              More data per candidate than any other platform.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-x-12 gap-y-14">
            {[
              {
                title: 'AI Interview Scores',
                description: 'Communication, problem solving, technical knowledge, growth mindset, and culture fit — scored by AI across multiple monthly interviews.',
              },
              {
                title: 'GitHub Deep Analysis',
                description: 'Not just repo counts. We analyze code originality, AI-assisted vs. hand-written code, contribution patterns, and project authenticity.',
              },
              {
                title: 'Vibe Code Review',
                description: 'See how candidates use AI coding tools. Are they architects or copy-pasters? Review their actual Cursor, Claude, and Copilot sessions.',
              },
              {
                title: 'Transcript Analysis',
                description: 'Course rigor scoring, GPA calibration across universities, and grade trajectory over semesters.',
              },
              {
                title: 'Growth Trajectory',
                description: 'Watch candidates improve interview-over-interview. Identify fast learners who will ramp up quickly on the job.',
              },
              {
                title: 'Skill Gap Matching',
                description: 'Automatic matching against your job requirements. See exactly which skills a candidate has, which they\'re close on, and which are missing.',
              },
            ].map((feature, i) => (
              <div key={feature.title} className="group">
                <h3 className="font-medium text-white mb-2.5 group-hover:text-teal-200 transition-colors duration-300">{feature.title}</h3>
                <p className="text-sm text-stone-400 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Sample profile preview */}
      <section className="py-32 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-[11px] font-medium text-stone-400 uppercase tracking-[0.2em] mb-4">Sample candidate</p>
            <h2 className="text-2xl font-semibold text-stone-900 mb-4">
              What an employer sees
            </h2>
          </div>

          <div className="bg-stone-50 rounded-2xl p-8 md:p-12 border border-stone-200">
            <div className="flex items-start gap-6 mb-8">
              <div className="w-14 h-14 bg-stone-200 rounded-full flex items-center justify-center text-stone-500 text-lg font-medium">
                JD
              </div>
              <div>
                <h3 className="text-lg font-semibold text-stone-900">Jane Doe</h3>
                <p className="text-sm text-stone-500">UC Berkeley &middot; CS &middot; Class of 2026</p>
              </div>
            </div>

            <div className="grid md:grid-cols-4 gap-4 mb-8">
              {[
                { label: 'Interview Score', value: '8.2/10', sub: '4 interviews, improving' },
                { label: 'GitHub Analysis', value: '92% organic', sub: '12 repos, 847 commits' },
                { label: 'Builder Profile', value: 'Architect', sub: 'Vibe code: 8.5/10' },
                { label: 'Transcript', value: '3.78 GPA', sub: 'High rigor courses' },
              ].map((stat) => (
                <div key={stat.label} className="bg-white rounded-xl p-4 border border-stone-200">
                  <p className="text-xs text-stone-400 mb-1">{stat.label}</p>
                  <p className="text-lg font-semibold text-stone-900">{stat.value}</p>
                  <p className="text-xs text-stone-500 mt-1">{stat.sub}</p>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-3">
              <span className="text-xs bg-teal-100 text-teal-700 px-3 py-1 rounded-full font-medium">Engineering</span>
              <span className="text-xs bg-stone-100 text-stone-600 px-3 py-1 rounded-full">Python</span>
              <span className="text-xs bg-stone-100 text-stone-600 px-3 py-1 rounded-full">React</span>
              <span className="text-xs bg-stone-100 text-stone-600 px-3 py-1 rounded-full">AWS</span>
              <span className="text-xs text-stone-400 ml-2">+ 5 more</span>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-32 px-6 bg-stone-50/50">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-2xl font-semibold text-stone-900 mb-4">
              How it works
            </h2>
          </div>

          <div className="space-y-10">
            {[
              {
                step: '1',
                title: 'Create your employer account',
                description: 'Sign up in 2 minutes. Add your open roles and requirements.',
              },
              {
                step: '2',
                title: 'Browse pre-vetted candidates',
                description: 'Filter by vertical (Engineering, Data, Business, Design), university, graduation year, and minimum score.',
              },
              {
                step: '3',
                title: 'Review rich profiles',
                description: 'Watch interview clips, review GitHub analysis, see growth trajectory charts, and read AI-generated summaries.',
              },
              {
                step: '4',
                title: 'Contact the best fits',
                description: 'Reach out directly to candidates who match your requirements. They\'re already interested and interview-ready.',
              },
            ].map((item) => (
              <div key={item.step} className="flex gap-6">
                <div className="w-10 h-10 bg-stone-900 text-white rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                  {item.step}
                </div>
                <div>
                  <h3 className="font-semibold text-stone-900 mb-1">{item.title}</h3>
                  <p className="text-stone-500 text-sm">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-32 px-6 bg-white">
        <div className="max-w-2xl mx-auto text-center">
          <p className="text-[11px] font-medium text-stone-400 uppercase tracking-[0.2em] mb-4">Pricing</p>
          <h2 className="text-2xl font-semibold text-stone-900 mb-4">
            Free during beta
          </h2>
          <p className="text-stone-500 mb-10">
            We're onboarding our first cohort of employers. Browse the full talent pool,
            view unlimited profiles, and contact candidates — all free while we're in beta.
          </p>
          <Link
            href="/employer/login"
            className="inline-flex items-center justify-center px-10 py-4 text-sm font-medium text-white bg-stone-900 rounded-full hover:bg-stone-800 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl"
          >
            Get Early Access
          </Link>
          <p className="mt-8 text-xs text-stone-400">
            No credit card required. Instant access to the talent pool.
          </p>
        </div>
      </section>

      <Footer />
    </main>
  )
}
