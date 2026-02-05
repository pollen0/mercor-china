'use client'

import { useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { setAuthTokens } from '@/lib/auth'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/candidates/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(data.detail || 'Invalid email or password')
      }

      const data = await response.json()

      // Store candidate info
      localStorage.setItem('candidate', JSON.stringify({
        id: data.candidate.id,
        name: data.candidate.name,
        email: data.candidate.email,
      }))

      // Store tokens (in both localStorage and cookies for middleware)
      setAuthTokens('candidate', {
        token: data.token,
        refreshToken: data.refresh_token,
        expiresIn: data.expires_in || 3600,
      })

      // Redirect to returnTo URL or dashboard
      const returnTo = searchParams.get('returnTo')
      router.push(returnTo || '/candidate/dashboard')

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="space-y-4">
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

        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="password" className="text-stone-600 text-sm">Password</Label>
            <Link href="/forgot-password" className="text-xs text-stone-500 hover:text-stone-700">
              Forgot password?
            </Link>
          </div>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Your password"
            required
            className="border-stone-200 focus:border-stone-400 focus:ring-0"
          />
        </div>

        {error && (
          <p className="text-sm text-red-500">{error}</p>
        )}

        <div className="pt-2">
          <Button
            type="submit"
            disabled={isLoading || !email || !password}
            className="w-full bg-stone-900 hover:bg-stone-800 text-white rounded-full h-11"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </Button>
        </div>
      </form>

      <p className="mt-8 text-center text-sm text-stone-400">
        Don&apos;t have an account?{' '}
        <Link href="/register" className="text-stone-900 hover:text-stone-600">
          Get started
        </Link>
      </p>

      <p className="mt-4 text-center text-sm text-stone-400">
        Are you an employer?{' '}
        <Link href="/employer/login" className="text-stone-900 hover:text-stone-600">
          Sign in here
        </Link>
      </p>
    </div>
  )
}

export default function CandidateLoginPage() {
  return (
    <main className="min-h-screen bg-white flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block text-xl font-semibold text-stone-900 mb-6 hover:text-stone-600 transition-colors">
            Pathway
          </Link>
          <h1 className="text-2xl font-semibold text-stone-900 mb-2">Welcome back, Student</h1>
          <p className="text-stone-400 text-sm">
            Sign in to continue your journey
          </p>
        </div>

        <Suspense fallback={<div className="animate-pulse h-64 bg-stone-100 rounded-lg" />}>
          <LoginForm />
        </Suspense>
      </div>
    </main>
  )
}
