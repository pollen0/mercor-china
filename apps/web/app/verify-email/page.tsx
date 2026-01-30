'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function VerifyEmailPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')
  const userType = searchParams.get('type') || 'candidate'

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('Missing verification token / 缺少验证令牌')
      return
    }

    verifyEmail()
  }, [token, userType])

  const verifyEmail = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          user_type: userType,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setStatus('success')
        setMessage(data.message || 'Email verified successfully!')
        setEmail(data.email || '')
      } else {
        setStatus('error')
        setMessage(data.detail || 'Verification failed')
      }
    } catch (error) {
      setStatus('error')
      setMessage('Network error. Please try again.')
    }
  }

  const getRedirectPath = () => {
    if (userType === 'employer') {
      return '/login'
    }
    return '/candidate/login'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-warm-50 to-warm-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          {status === 'loading' && (
            <>
              <div className="w-16 h-16 mx-auto mb-4">
                <div className="w-16 h-16 border-4 border-warm-200 border-t-brand-500 rounded-full animate-spin" />
              </div>
              <CardTitle className="text-xl">Verifying your email...</CardTitle>
              <CardDescription>正在验证您的邮箱...</CardDescription>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <CardTitle className="text-xl text-green-600">Email Verified!</CardTitle>
              <CardDescription>邮箱验证成功!</CardDescription>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <CardTitle className="text-xl text-red-600">Verification Failed</CardTitle>
              <CardDescription>验证失败</CardDescription>
            </>
          )}
        </CardHeader>

        <CardContent className="text-center space-y-4">
          <p className="text-warm-600">{message}</p>

          {status === 'success' && email && (
            <p className="text-sm text-warm-500">
              Verified email: <span className="font-medium">{email}</span>
            </p>
          )}

          {status === 'success' && (
            <div className="pt-4">
              <Link href={getRedirectPath()}>
                <Button variant="brand" className="w-full">
                  {userType === 'employer' ? 'Go to Login' : 'Continue to Login'}
                </Button>
              </Link>
            </div>
          )}

          {status === 'error' && (
            <div className="pt-4 space-y-3">
              <Button
                variant="outline"
                className="w-full"
                onClick={() => router.push(getRedirectPath())}
              >
                Go to Login
              </Button>
              <p className="text-xs text-warm-500">
                Need a new verification link? Login and request a new one from your dashboard.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
