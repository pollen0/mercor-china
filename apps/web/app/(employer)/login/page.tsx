'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { employerApi } from '@/lib/api'

type Mode = 'login' | 'register'

export default function EmployerLoginPage() {
  const router = useRouter()
  const [mode, setMode] = useState<Mode>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      if (mode === 'login') {
        const result = await employerApi.login(email, password)
        localStorage.setItem('employer_token', result.token)
        localStorage.setItem('employer', JSON.stringify(result.employer))
        router.push('/dashboard')
      } else {
        const result = await employerApi.register({
          companyName,
          email,
          password,
        })
        localStorage.setItem('employer_token', result.token)
        localStorage.setItem('employer', JSON.stringify(result.employer))
        router.push('/dashboard')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:flex-1 lg:flex-col justify-center px-12 bg-gradient-to-br from-emerald-600 to-teal-700">
        <div className="max-w-md">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-xl">智</span>
            </div>
            <span className="text-white font-semibold text-2xl">ZhiMian 智面</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-6">
            Screen candidates 10x faster with AI
          </h1>
          <p className="text-emerald-100 text-lg leading-relaxed mb-8">
            Automated 15-minute video interviews with intelligent scoring.
            Built for New Energy/EV and Sales verticals in China.
          </p>
          <div className="space-y-4">
            {[
              'AI-powered 5-dimension scoring',
              'Vertical-specific interview questions',
              'Mandarin speech-to-text transcription',
              'Ranked candidate recommendations',
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-3 text-white/90">
                <svg className="w-5 h-5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold">智</span>
              </div>
              <span className="text-gray-900 font-semibold text-xl">ZhiMian 智面</span>
            </Link>
          </div>

          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">
                {mode === 'login' ? 'Welcome back' : 'Create your account'}
              </h2>
              <p className="text-gray-500 mt-2">
                {mode === 'login'
                  ? 'Sign in to access your employer dashboard'
                  : 'Start screening candidates smarter'}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {mode === 'register' && (
                <div>
                  <Label htmlFor="companyName" className="text-sm font-medium text-gray-700">
                    Company Name
                  </Label>
                  <Input
                    id="companyName"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="Your company name"
                    className="mt-2 h-12"
                    required
                  />
                </div>
              )}

              <div>
                <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  className="mt-2 h-12"
                  required
                />
              </div>

              <div>
                <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Password
                </Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="mt-2 h-12"
                  required
                  minLength={8}
                />
              </div>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <Button
                type="submit"
                className="w-full h-12 bg-emerald-600 hover:bg-emerald-700 text-base font-medium"
                disabled={isLoading}
              >
                {isLoading
                  ? 'Please wait...'
                  : mode === 'login'
                  ? 'Sign In'
                  : 'Create Account'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={() => {
                  setMode(mode === 'login' ? 'register' : 'login')
                  setError(null)
                }}
                className="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
              >
                {mode === 'login'
                  ? "Don't have an account? Register"
                  : 'Already have an account? Sign in'}
              </button>
            </div>
          </div>

          <p className="mt-8 text-center text-sm text-gray-500">
            By continuing, you agree to ZhiMian&apos;s Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </main>
  )
}
