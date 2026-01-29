import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">智</span>
              </div>
              <span className="font-semibold text-gray-900 text-lg">ZhiMian 智面</span>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/login"
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              >
                Employer Login
              </Link>
              <Link
                href="/login"
                className="text-sm font-medium text-white bg-gray-900 hover:bg-gray-800 px-4 py-2 rounded-lg transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-sm font-medium mb-6">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              AI-Powered Recruiting for China
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
              Screen candidates 10x faster with
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600"> AI video interviews</span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 mb-8 leading-relaxed">
              Cut screening time from weeks to hours. Automated 15-minute AI interviews with intelligent scoring.
              Built for New Energy/EV and Sales verticals in China.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/login"
                className="inline-flex items-center justify-center px-6 py-3.5 text-base font-medium text-white bg-gray-900 rounded-xl hover:bg-gray-800 transition-all shadow-lg shadow-gray-900/10"
              >
                Start Free Trial
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </Link>
              <Link
                href="#verticals"
                className="inline-flex items-center justify-center px-6 py-3.5 text-base font-medium text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 transition-all"
              >
                Explore Verticals
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-gray-900 mb-1">10x</div>
              <div className="text-sm text-gray-600">Faster Screening</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-gray-900 mb-1">15min</div>
              <div className="text-sm text-gray-600">AI Interview</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-gray-900 mb-1">5</div>
              <div className="text-sm text-gray-600">Scoring Dimensions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-gray-900 mb-1">24/7</div>
              <div className="text-sm text-gray-600">Async Interviews</div>
            </div>
          </div>
        </div>
      </section>

      {/* Verticals Section */}
      <section id="verticals" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Built for High-Growth Industries
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Specialized AI interview templates for New Energy/EV and Sales verticals
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 lg:gap-12">
            {/* New Energy/EV Vertical */}
            <div className="bg-white border border-gray-200 rounded-2xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-emerald-50 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-7 h-7 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">New Energy / EV</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Assess technical depth and industry knowledge for the booming EV sector.
                300k+ job gap and huge talent shortage.
              </p>
              <div className="space-y-3">
                {[
                  { role: 'Battery Engineer', assessment: 'Technical knowledge tests' },
                  { role: 'Embedded Software', assessment: 'Coding + domain questions' },
                  { role: 'Autonomous Driving', assessment: 'Algorithm + simulation' },
                  { role: 'Supply Chain', assessment: 'Case studies' },
                  { role: 'EV Sales', assessment: 'Role-play, product knowledge' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                    <span className="text-sm font-medium text-gray-900">{item.role}</span>
                    <span className="text-xs text-gray-500">{item.assessment}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Sales/BD Vertical */}
            <div className="bg-white border border-gray-200 rounded-2xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-blue-50 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Sales / BD</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Evaluate persuasion skills, objection handling, and customer rapport.
                High turnover means constant hiring needs.
              </p>
              <div className="space-y-3">
                {[
                  { role: 'Sales Representative', assessment: 'Role-play scenarios' },
                  { role: 'BD Manager', assessment: 'Strategy + negotiation' },
                  { role: 'Account Manager', assessment: 'Relationship building' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                    <span className="text-sm font-medium text-gray-900">{item.role}</span>
                    <span className="text-xs text-gray-500">{item.assessment}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              How ZhiMian Works
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Three simple steps to transform your hiring process
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
            <div className="relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-emerald-600 text-white rounded-2xl flex items-center justify-center text-xl font-bold shadow-lg shadow-emerald-600/30">
                1
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl p-8 pt-12 h-full hover:shadow-lg transition-shadow">
                <div className="w-14 h-14 bg-emerald-50 rounded-xl flex items-center justify-center mb-6">
                  <svg className="w-7 h-7 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Create Job & Select Vertical</h3>
                <p className="text-gray-600 leading-relaxed">
                  Choose your industry vertical and role type. AI automatically selects the best interview questions.
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-teal-600 text-white rounded-2xl flex items-center justify-center text-xl font-bold shadow-lg shadow-teal-600/30">
                2
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl p-8 pt-12 h-full hover:shadow-lg transition-shadow">
                <div className="w-14 h-14 bg-teal-50 rounded-xl flex items-center justify-center mb-6">
                  <svg className="w-7 h-7 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Share Interview Link</h3>
                <p className="text-gray-600 leading-relaxed">
                  Generate unique links for candidates. They complete a 15-minute AI video interview anytime.
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-blue-600 text-white rounded-2xl flex items-center justify-center text-xl font-bold shadow-lg shadow-blue-600/30">
                3
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl p-8 pt-12 h-full hover:shadow-lg transition-shadow">
                <div className="w-14 h-14 bg-blue-50 rounded-xl flex items-center justify-center mb-6">
                  <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Review AI Scores</h3>
                <p className="text-gray-600 leading-relaxed">
                  Get ranked candidates with scores on 5 dimensions. Watch videos, read transcripts, and decide fast.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AI Scoring Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                5-Dimensional AI Scoring
              </h2>
              <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                Our GPT-4o powered AI evaluates each candidate response across five key dimensions,
                providing objective and consistent assessments at scale.
              </p>
              <div className="space-y-4">
                {[
                  { name: '沟通能力 Communication', desc: 'Clarity, structure, and fluency' },
                  { name: '解决问题 Problem Solving', desc: 'Logical reasoning and analytical thinking' },
                  { name: '专业知识 Domain Knowledge', desc: 'Technical depth and industry awareness' },
                  { name: '动机 Motivation', desc: 'Genuine interest and career alignment' },
                  { name: '文化契合 Culture Fit', desc: 'Values alignment and team orientation' },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-4">
                    <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                      <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <div className="font-medium text-white">{item.name}</div>
                      <div className="text-sm text-gray-400">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white/5 rounded-2xl p-8 border border-white/10">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <div className="text-sm text-gray-400">Overall Score</div>
                  <div className="text-4xl font-bold text-emerald-400">82/100</div>
                </div>
                <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center">
                  <svg className="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div className="space-y-3">
                {[
                  { name: 'Communication', score: 85 },
                  { name: 'Problem Solving', score: 78 },
                  { name: 'Domain Knowledge', score: 88 },
                  { name: 'Motivation', score: 82 },
                  { name: 'Culture Fit', score: 80 },
                ].map((item, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">{item.name}</span>
                      <span className="text-white font-medium">{item.score}%</span>
                    </div>
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-500"
                        style={{ width: `${item.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Ready to transform your hiring?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Join companies using AI to hire smarter and faster in China&apos;s fastest-growing industries.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-gray-900 rounded-xl hover:bg-gray-800 transition-all shadow-lg shadow-gray-900/10"
          >
            Get Started Free
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-gray-100">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-md flex items-center justify-center">
              <span className="text-white font-bold text-xs">智</span>
            </div>
            <span className="font-medium text-gray-900">ZhiMian 智面</span>
          </div>
          <div className="text-sm text-gray-500">
            &copy; {new Date().getFullYear()} ZhiMian. All rights reserved.
          </div>
        </div>
      </footer>
    </main>
  )
}
