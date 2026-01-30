'use client'

import { Suspense, useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function VerifyEmailContent() {
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
      setMessage('Missing verification token')
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
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        {status === 'loading' && (
          <>
            <div className="w-14 h-14 mx-auto mb-4">
              <div className="w-14 h-14 border-2 border-warm-200 border-t-brand-500 rounded-full animate-spin" />
            </div>
            <CardTitle className="text-lg">Verifying...</CardTitle>
            <CardDescription>Please wait</CardDescription>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="w-14 h-14 mx-auto mb-4 bg-brand-50 rounded-full flex items-center justify-center">
              <svg className="w-7 h-7 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <CardTitle className="text-lg">Email Verified</CardTitle>
            <CardDescription>You can now sign in</CardDescription>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-14 h-14 mx-auto mb-4 bg-warm-100 rounded-full flex items-center justify-center">
              <svg className="w-7 h-7 text-warm-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <CardTitle className="text-lg">Verification Failed</CardTitle>
            <CardDescription>Please try again</CardDescription>
          </>
        )}
      </CardHeader>

      <CardContent className="text-center space-y-4">
        <p className="text-warm-600 text-sm">{message}</p>

        {status === 'success' && email && (
          <p className="text-sm text-warm-500">
            Verified: <span className="font-medium">{email}</span>
          </p>
        )}

        {status === 'success' && (
          <div className="pt-2">
            <Link href={getRedirectPath()}>
              <Button variant="brand" className="w-full">
                Continue to Login
              </Button>
            </Link>
          </div>
        )}

        {status === 'error' && (
          <div className="pt-2">
            <Button
              variant="outline"
              className="w-full"
              onClick={() => router.push(getRedirectPath())}
            >
              Go to Login
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function LoadingState() {
  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <div className="w-14 h-14 mx-auto mb-4">
          <div className="w-14 h-14 border-2 border-warm-200 border-t-brand-500 rounded-full animate-spin" />
        </div>
        <CardTitle className="text-lg">Loading...</CardTitle>
      </CardHeader>
    </Card>
  )
}

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen bg-warm-50 flex items-center justify-center p-4">
      <Suspense fallback={<LoadingState />}>
        <VerifyEmailContent />
      </Suspense>
    </div>
  )
}
