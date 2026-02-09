'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { authApi } from '@/lib/api'

type UserType = 'candidate' | 'employer'

function ResetPasswordForm() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const token = searchParams.get('token')
  const userType = (searchParams.get('type') as UserType) || 'candidate'

  useEffect(() => {
    if (!token) {
      setError('Invalid reset link. Please request a new password reset.')
    }
  }, [token])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    if (!token) {
      setError('Invalid reset link')
      return
    }

    setIsLoading(true)

    try {
      await authApi.resetPassword(token, userType, password)
      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset password')
    } finally {
      setIsLoading(false)
    }
  }

  if (!token) {
    return (
      <main className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h1 className="text-2xl font-semibold text-stone-900 mb-2">Invalid reset link</h1>
            <p className="text-stone-500 text-sm">
              This password reset link is invalid or has expired.
            </p>
          </div>

          <Link href="/forgot-password">
            <Button className="w-full bg-stone-900 hover:bg-stone-800 text-white rounded-full h-11">
              Request new reset link
            </Button>
          </Link>
        </div>
      </main>
    )
  }

  if (success) {
    return (
      <main className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-teal-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-semibold text-stone-900 mb-2">Password reset successful</h1>
            <p className="text-stone-500 text-sm">
              Your password has been changed. You can now sign in with your new password.
            </p>
          </div>

          <Link href={userType === 'candidate' ? '/candidate/login' : '/employer/login'}>
            <Button className="w-full bg-stone-900 hover:bg-stone-800 text-white rounded-full h-11">
              Sign in
            </Button>
          </Link>
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
          <h1 className="text-2xl font-semibold text-stone-900 mb-2">Set new password</h1>
          <p className="text-stone-400 text-sm">
            Enter your new password below.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="password" className="text-stone-600 text-sm">New password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              required
              minLength={8}
              className="border-stone-200 focus:border-stone-400 focus:ring-0"
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="confirmPassword" className="text-stone-600 text-sm">Confirm password</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
              required
              minLength={8}
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
              disabled={isLoading || !password || !confirmPassword}
              className="w-full bg-stone-900 hover:bg-stone-800 text-white rounded-full h-11"
            >
              {isLoading ? 'Resetting...' : 'Reset password'}
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

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <div className="w-8 h-8 border-2 border-stone-200 border-t-stone-600 rounded-full animate-spin mx-auto" />
        </div>
      </main>
    }>
      <ResetPasswordForm />
    </Suspense>
  )
}
