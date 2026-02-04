'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { authApi, ApiError } from '@/lib/api'

interface EmployerVerificationBannerProps {
  email: string
  onDismiss?: () => void
}

export function EmployerVerificationBanner({ email, onDismiss }: EmployerVerificationBannerProps) {
  const [isResending, setIsResending] = useState(false)
  const [resendSuccess, setResendSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDismissed, setIsDismissed] = useState(false)

  const handleResend = async () => {
    setIsResending(true)
    setError(null)
    setResendSuccess(false)

    try {
      await authApi.resendVerification(email, 'employer')
      setResendSuccess(true)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to resend verification email. Please try again.')
      }
    } finally {
      setIsResending(false)
    }
  }

  const handleDismiss = () => {
    setIsDismissed(true)
    onDismiss?.()
  }

  if (isDismissed) {
    return null
  }

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg className="w-5 h-5 text-amber-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-amber-800">
            Verify your email address
          </h3>
          <p className="text-sm text-amber-700 mt-1">
            Please check your inbox and click the verification link we sent to <span className="font-medium">{email}</span>.
            Verified employers can access all platform features.
          </p>

          {error && (
            <p className="text-sm text-red-600 mt-2">{error}</p>
          )}

          {resendSuccess && (
            <p className="text-sm text-green-600 mt-2">
              Verification email sent! Please check your inbox.
            </p>
          )}

          <div className="flex items-center gap-3 mt-3">
            <Button
              size="sm"
              variant="outline"
              onClick={handleResend}
              disabled={isResending || resendSuccess}
              className="text-amber-700 border-amber-300 hover:bg-amber-100"
            >
              {isResending ? (
                <>
                  <span className="w-3 h-3 border-2 border-amber-600 border-t-transparent rounded-full animate-spin mr-2" />
                  Sending...
                </>
              ) : resendSuccess ? (
                <>
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Sent!
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Resend Email
                </>
              )}
            </Button>
            <button
              onClick={handleDismiss}
              className="text-sm text-amber-600 hover:text-amber-800"
            >
              Dismiss
            </button>
          </div>
        </div>
        <button
          onClick={handleDismiss}
          className="flex-shrink-0 text-amber-400 hover:text-amber-600"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  )
}
