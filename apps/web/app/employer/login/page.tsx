'use client'

import { useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { employerApi } from '@/lib/api'
import { setAuthTokens } from '@/lib/auth'

type Mode = 'login' | 'register'

function EmployerLoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [mode, setMode] = useState<Mode>('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Check passwords match for registration
    if (mode === 'register' && password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setIsLoading(true)

    try {
      let result
      if (mode === 'login') {
        result = await employerApi.login(email, password)
      } else {
        result = await employerApi.register({
          name: name || undefined,
          companyName,
          email,
          password,
        })
      }

      // Store employer info
      localStorage.setItem('employer', JSON.stringify(result.employer))

      // Store tokens (in both localStorage and cookies for middleware)
      setAuthTokens('employer', {
        token: result.token,
        refreshToken: (result as { refresh_token?: string }).refresh_token,
        expiresIn: (result as { expires_in?: number }).expires_in || 3600,
      })

      // Redirect to returnTo URL or talent pool (default view for employers)
      const returnTo = searchParams.get('returnTo')
      router.push(returnTo || '/dashboard?tab=talent')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-3xl shadow-soft-lg border border-stone-100 p-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-stone-900">
          {mode === 'login' ? 'Welcome back' : 'Create your account'}
        </h2>
        <p className="text-stone-500 mt-2">
          {mode === 'login'
            ? 'Sign in to access your employer dashboard'
            : 'Start screening candidates smarter'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {mode === 'register' && (
          <>
            <div>
              <Label htmlFor="name" className="text-sm font-medium text-stone-700">
                Your Name
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Smith"
                className="mt-2"
                required
              />
            </div>
            <div>
              <Label htmlFor="companyName" className="text-sm font-medium text-stone-700">
                Company Name
              </Label>
              <Input
                id="companyName"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Your company name"
                className="mt-2"
                required
              />
            </div>
          </>
        )}

        <div>
          <Label htmlFor="email" className="text-sm font-medium text-stone-700">
            Email
          </Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            className="mt-2"
            required
          />
        </div>

        <div>
          <div className="flex items-center justify-between">
            <Label htmlFor="password" className="text-sm font-medium text-stone-700">
              Password
            </Label>
            {mode === 'login' && (
              <Link href="/forgot-password" className="text-xs text-stone-500 hover:text-teal-600">
                Forgot password?
              </Link>
            )}
          </div>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            className="mt-2"
            required
            minLength={8}
          />
        </div>

        {mode === 'register' && (
          <div>
            <Label htmlFor="confirmPassword" className="text-sm font-medium text-stone-700">
              Confirm Password
            </Label>
            <Input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
              className="mt-2"
              required
              minLength={8}
            />
          </div>
        )}

        {error && (
          <div className="p-4 bg-error-light border border-error/20 rounded-xl">
            <p className="text-sm text-error-dark">{error}</p>
          </div>
        )}

        <Button
          type="submit"
          variant="default"
          className="w-full"
          disabled={isLoading}
          loading={isLoading}
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
            setConfirmPassword('')
          }}
          className="text-sm text-teal-600 hover:text-teal-700 font-medium"
        >
          {mode === 'login'
            ? "Don't have an account? Register"
            : 'Already have an account? Sign in'}
        </button>
      </div>
    </div>
  )
}

export default function EmployerLoginPage() {
  return (
    <main className="min-h-screen bg-stone-50 flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:flex-1 lg:flex-col justify-center px-12 bg-gradient-to-br from-teal-600 to-teal-500">
        <div className="max-w-md">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <span className="text-white font-semibold text-2xl">Pathway</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-6 leading-tight">
            Hire top college talent based on growth trajectory
          </h1>
          <p className="text-teal-100 text-lg leading-relaxed mb-8">
            See how candidates improve over time with monthly AI interviews.
            Hire students from top CS programs — MIT, Stanford, Berkeley, CMU, and more.
          </p>
          <div className="space-y-4">
            {[
              'AI-powered 5-dimension scoring',
              'Track candidate growth over time',
              'GitHub integration for technical roles',
              'Filter by university and graduation year',
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-3 text-white/90">
                <svg className="w-5 h-5 text-teal-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
              <div className="w-10 h-10 bg-teal-600 rounded-xl flex items-center justify-center shadow-lg">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <span className="text-stone-900 font-semibold text-xl">Pathway</span>
            </Link>
          </div>

          <Suspense fallback={<div className="animate-pulse h-96 bg-stone-100 rounded-3xl" />}>
            <EmployerLoginForm />
          </Suspense>

          <p className="mt-8 text-center text-sm text-stone-500">
            By continuing, you agree to Pathway&apos;s Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </main>
  )
}
