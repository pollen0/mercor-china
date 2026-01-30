import Link from 'next/link'
import { Navbar } from '@/components/layout/navbar'
import { Footer } from '@/components/layout/footer'
import { Container, Section, PageWrapper } from '@/components/layout/container'

export default function Home() {
  return (
    <PageWrapper navbarOffset={true}>
      <Navbar />

      {/* Hero Section - Split for Candidates and Employers */}
      <Section size="lg" className="pt-12">
        <Container>
          {/* Main headline */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-50 text-brand-700 text-sm font-medium mb-8">
              <span className="w-2 h-2 bg-brand-500 rounded-full animate-pulse"></span>
              AI-Powered Recruiting for China
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-warm-900 leading-tight mb-6 text-balance">
              The future of hiring in
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-500 to-brand-600"> New Energy & Sales</span>
            </h1>
            <p className="text-lg sm:text-xl text-warm-600 max-w-3xl mx-auto leading-relaxed">
              15-minute AI video interviews that match top talent with leading companies in China&apos;s fastest-growing industries.
            </p>
          </div>

          {/* Two CTAs - Candidate and Employer */}
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Candidate CTA */}
            <div className="bg-gradient-to-br from-brand-50 to-brand-100/50 border border-brand-100 rounded-3xl p-8 text-center hover:shadow-soft-lg transition-all duration-300 group">
              <div className="w-16 h-16 bg-gradient-to-br from-brand-500 to-brand-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-brand group-hover:shadow-brand-lg transition-shadow">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-warm-900 mb-3">I&apos;m looking for a job</h2>
              <p className="text-warm-600 mb-8 leading-relaxed">
                Take a 15-minute AI interview and get matched with top companies in New Energy, EV, and Sales.
              </p>
              <Link
                href="/candidate/register"
                className="inline-flex items-center justify-center w-full px-6 py-4 text-base font-semibold text-white bg-gradient-to-r from-brand-500 to-brand-600 rounded-xl hover:from-brand-600 hover:to-brand-700 transition-all shadow-brand hover:shadow-brand-lg hover:scale-[1.02] active:scale-[0.98]"
              >
                Start Interview
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </Link>
              <p className="text-sm text-warm-500 mt-4">
                Already have an account? <Link href="/candidate/login" className="text-brand-600 hover:text-brand-700 font-medium">Sign in</Link>
              </p>
            </div>

            {/* Employer CTA */}
            <div className="bg-gradient-to-br from-warm-50 to-warm-100/50 border border-warm-200 rounded-3xl p-8 text-center hover:shadow-soft-lg transition-all duration-300 group">
              <div className="w-16 h-16 bg-warm-900 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-soft-md group-hover:shadow-soft-lg transition-shadow">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-warm-900 mb-3">I&apos;m hiring talent</h2>
              <p className="text-warm-600 mb-8 leading-relaxed">
                Screen candidates 10x faster with AI interviews. Get scored results with video, transcript, and analysis.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center justify-center w-full px-6 py-4 text-base font-semibold text-white bg-warm-900 rounded-xl hover:bg-warm-800 transition-all shadow-soft-md hover:shadow-soft-lg hover:scale-[1.02] active:scale-[0.98]"
              >
                Post a Job
                <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </Link>
              <p className="text-sm text-warm-500 mt-4">
                Already have an account? <Link href="/login" className="text-warm-900 hover:text-warm-700 font-medium">Sign in</Link>
              </p>
            </div>
          </div>
        </Container>
      </Section>

      {/* Stats Section */}
      <Section size="sm" className="bg-warm-50 border-y border-warm-100">
        <Container>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-warm-900 mb-1">10x</div>
              <div className="text-sm text-warm-600">Faster Screening</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-warm-900 mb-1">15min</div>
              <div className="text-sm text-warm-600">AI Interview</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-warm-900 mb-1">5</div>
              <div className="text-sm text-warm-600">Scoring Dimensions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-warm-900 mb-1">24/7</div>
              <div className="text-sm text-warm-600">Async Interviews</div>
            </div>
          </div>
        </Container>
      </Section>

      {/* How It Works - For Candidates */}
      <Section size="lg">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-warm-900 mb-4">
              How It Works for Candidates
            </h2>
            <p className="text-lg text-warm-600 max-w-2xl mx-auto">
              Get discovered by top companies in three simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
            <div className="relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-brand-500 text-white rounded-2xl flex items-center justify-center text-xl font-bold shadow-brand">
                1
              </div>
              <div className="bg-white border border-warm-200 rounded-2xl p-8 pt-12 h-full shadow-soft hover:shadow-soft-md transition-shadow">
                <h3 className="text-xl font-semibold text-warm-900 mb-3">Create Your Profile</h3>
                <p className="text-warm-600 leading-relaxed">
                  Sign up with your basic info and select the roles you&apos;re interested in.
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-brand-500 text-white rounded-2xl flex items-center justify-center text-xl font-bold shadow-brand">
                2
              </div>
              <div className="bg-white border border-warm-200 rounded-2xl p-8 pt-12 h-full shadow-soft hover:shadow-soft-md transition-shadow">
                <h3 className="text-xl font-semibold text-warm-900 mb-3">Complete AI Interview</h3>
                <p className="text-warm-600 leading-relaxed">
                  Answer 5 video questions in about 15 minutes. Our AI analyzes your responses.
                </p>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-brand-500 text-white rounded-2xl flex items-center justify-center text-xl font-bold shadow-brand">
                3
              </div>
              <div className="bg-white border border-warm-200 rounded-2xl p-8 pt-12 h-full shadow-soft hover:shadow-soft-md transition-shadow">
                <h3 className="text-xl font-semibold text-warm-900 mb-3">Get Matched</h3>
                <p className="text-warm-600 leading-relaxed">
                  Your profile is visible to employers. Get contacted for roles that match your skills.
                </p>
              </div>
            </div>
          </div>
        </Container>
      </Section>

      {/* Verticals Section */}
      <Section id="verticals" size="lg" className="bg-warm-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-warm-900 mb-4">
              Focus Industries
            </h2>
            <p className="text-lg text-warm-600 max-w-2xl mx-auto">
              Specialized for China&apos;s highest-growth sectors
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 lg:gap-12">
            {/* New Energy/EV */}
            <div className="bg-white border border-warm-200 rounded-2xl p-8 hover:shadow-soft-md transition-all duration-300 shadow-soft">
              <div className="w-14 h-14 bg-brand-50 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-7 h-7 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-warm-900 mb-3">New Energy / EV 新能源</h3>
              <p className="text-warm-600 mb-6 leading-relaxed">
                Battery Engineers, Embedded Software, Autonomous Driving, Supply Chain, EV Sales
              </p>
              <div className="text-sm text-brand-600 font-medium">300k+ job gap in China</div>
            </div>

            {/* Sales/BD */}
            <div className="bg-white border border-warm-200 rounded-2xl p-8 hover:shadow-soft-md transition-all duration-300 shadow-soft">
              <div className="w-14 h-14 bg-info-light rounded-xl flex items-center justify-center mb-6">
                <svg className="w-7 h-7 text-info" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-warm-900 mb-3">Sales / BD 销售</h3>
              <p className="text-warm-600 mb-6 leading-relaxed">
                Sales Representatives, BD Managers, Account Managers, Customer Success
              </p>
              <div className="text-sm text-info font-medium">High-volume hiring needs</div>
            </div>
          </div>
        </Container>
      </Section>

      {/* CTA Section */}
      <Section size="lg" className="bg-warm-900 text-white">
        <Container size="md">
          <div className="text-center">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Ready to get started?
            </h2>
            <p className="text-lg text-warm-400 mb-10">
              Whether you&apos;re looking for your next opportunity or hiring top talent.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/candidate/register"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-warm-900 bg-white rounded-xl hover:bg-warm-100 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                I&apos;m a Candidate
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white border border-white/30 rounded-xl hover:bg-white/10 transition-all"
              >
                I&apos;m an Employer
              </Link>
            </div>
          </div>
        </Container>
      </Section>

      <Footer />
    </PageWrapper>
  )
}
