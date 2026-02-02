'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function CandidateLoginPage() {
  const router = useRouter()
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

      localStorage.setItem('candidate', JSON.stringify({
        id: data.candidate.id,
        name: data.candidate.name,
        email: data.candidate.email,
      }))
      localStorage.setItem('candidate_token', data.token)

      router.push('/candidate/dashboard')

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  // GitHub login removed - users should connect GitHub from dashboard after registration

  return (
    <main className="min-h-screen bg-white flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block text-xl font-semibold text-gray-900 mb-6 hover:text-gray-600 transition-colors">
            Pathway
          </Link>
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">Welcome back, Student</h1>
          <p className="text-gray-400 text-sm">
            Sign in to continue your journey
          </p>
        </div>

        <div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email" className="text-gray-600 text-sm">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="border-gray-200 focus:border-gray-400 focus:ring-0"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password" className="text-gray-600 text-sm">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Your password"
                required
                className="border-gray-200 focus:border-gray-400 focus:ring-0"
              />
            </div>

            {error && (
              <p className="text-sm text-red-500">{error}</p>
            )}

            <div className="pt-2">
              <Button
                type="submit"
                disabled={isLoading || !email || !password}
                className="w-full bg-gray-900 hover:bg-gray-800 text-white rounded-full h-11"
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </Button>
            </div>
          </form>

          <p className="mt-8 text-center text-sm text-gray-400">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-gray-900 hover:text-gray-600">
              Get started
            </Link>
          </p>

          <p className="mt-4 text-center text-sm text-gray-400">
            Are you an employer?{' '}
            <Link href="/employer/login" className="text-gray-900 hover:text-gray-600">
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </main>
  )
}
