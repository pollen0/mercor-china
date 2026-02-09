'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { authApi } from '@/lib/api'

type UserType = 'candidate' | 'employer'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [userType, setUserType] = useState<UserType>('candidate')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      await authApi.forgotPassword(email, userType)
      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send reset email')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <main className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-teal-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h1 className="text-2xl font-semibold text-stone-900 mb-2">Check your email</h1>
            <p className="text-stone-500 text-sm">
              If an account exists with <span className="font-medium">{email}</span>, we&apos;ve sent a password reset link.
            </p>
          </div>

          <p className="text-stone-400 text-sm mb-6">
            The link will expire in 1 hour. Check your spam folder if you don&apos;t see it.
          </p>

          <div className="space-y-3">
            <Button
              variant="outline"
              onClick={() => {
                setSuccess(false)
                setEmail('')
              }}
              className="w-full"
            >
              Send another email
            </Button>
            <Link href={userType === 'candidate' ? '/candidate/login' : '/employer/login'}>
              <Button variant="ghost" className="w-full">
                Back to sign in
              </Button>
            </Link>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-white flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block text-xl font-semibold text-stone-900 mb-6 hover:text-stone-600 transition-colors">
            Pathway
          </Link>
          <h1 className="text-2xl font-semibold text-stone-900 mb-2">Forgot your password?</h1>
          <p className="text-stone-400 text-sm">
            Enter your email and we&apos;ll send you a reset link.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label className="text-stone-600 text-sm">I am a</Label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setUserType('candidate')}
                className={`flex-1 py-2.5 px-4 rounded-lg border text-sm font-medium transition-colors ${
                  userType === 'candidate'
                    ? 'border-teal-600 bg-teal-50 text-teal-700'
                    : 'border-stone-200 text-stone-600 hover:border-stone-300'
                }`}
              >
                Student
              </button>
              <button
                type="button"
                onClick={() => setUserType('employer')}
                className={`flex-1 py-2.5 px-4 rounded-lg border text-sm font-medium transition-colors ${
                  userType === 'employer'
                    ? 'border-teal-600 bg-teal-50 text-teal-700'
                    : 'border-stone-200 text-stone-600 hover:border-stone-300'
                }`}
              >
                Employer
              </button>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="email" className="text-stone-600 text-sm">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="border-stone-200 focus:border-stone-400 focus:ring-0"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-100 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="pt-2">
            <Button
              type="submit"
              disabled={isLoading || !email}
              className="w-full bg-stone-900 hover:bg-stone-800 text-white rounded-full h-11"
            >
              {isLoading ? 'Sending...' : 'Send reset link'}
            </Button>
          </div>
        </form>

        <p className="mt-8 text-center text-sm text-stone-400">
          Remember your password?{' '}
          <Link href={userType === 'candidate' ? '/candidate/login' : '/employer/login'} className="text-stone-900 hover:text-stone-600">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  )
}
