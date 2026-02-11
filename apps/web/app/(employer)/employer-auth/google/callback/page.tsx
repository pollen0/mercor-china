'use client'

import { Suspense, useEffect, useState, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { employerCalendarApi } from '@/lib/api'

function EmployerGoogleCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [errorMessage, setErrorMessage] = useState('')

  // Ref to prevent double execution (React Strict Mode runs effects twice)
  const isProcessingRef = useRef(false)

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')
      const errorDescription = searchParams.get('error_description')

      // CRITICAL: Prevent double execution - OAuth codes can only be used once
      if (isProcessingRef.current) {
        console.log('[Employer Google OAuth] Already processing, skipping duplicate call')
        return
      }

      // Also check sessionStorage for the specific code being processed
      const processingCode = sessionStorage.getItem('employer_google_oauth_processing')
      if (processingCode === code) {
        console.log('[Employer Google OAuth] This code is already being processed')
        return
      }

      // Check if employer is logged in
      const token = localStorage.getItem('employer_token')
      if (!token) {
        setStatus('error')
        setErrorMessage('You must be logged in to connect Google Calendar. Please log in and try again.')
        return
      }

      // Check for Google errors
      if (error) {
        setStatus('error')
        setErrorMessage(errorDescription || 'Google authorization was cancelled or failed')
        return
      }

      if (!code) {
        setStatus('error')
        setErrorMessage('No authorization code received. Please try again.')
        return
      }

      // Validate CSRF state token
      const savedState = sessionStorage.getItem('employer_google_oauth_state')
      if (state && savedState && state !== savedState) {
        setStatus('error')
        setErrorMessage('Security validation failed. Please try again.')
        return
      }

      // Mark as processing BEFORE clearing state and making API call
      isProcessingRef.current = true
      sessionStorage.setItem('employer_google_oauth_processing', code)

      // Clear the saved state
      sessionStorage.removeItem('employer_google_oauth_state')

      try {
        console.log('[Employer Google OAuth] Exchanging code for token...')

        // Exchange code for token and connect Google Calendar
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('Request timed out. Please try again.')), 30000)
        })

        await Promise.race([
          employerCalendarApi.connectGoogle(code, state || undefined),
          timeoutPromise
        ])

        console.log('[Employer Google OAuth] Successfully connected Google Calendar')
        setStatus('success')

        // Clear the processing marker on success
        sessionStorage.removeItem('employer_google_oauth_processing')

        // Redirect after a short delay to dashboard
        setTimeout(() => {
          router.push('/dashboard?google=connected')
        }, 2000)
      } catch (err) {
        console.error('[Employer Google OAuth] Connection error:', err)

        // Clear the processing marker on error so user can retry
        sessionStorage.removeItem('employer_google_oauth_processing')
        isProcessingRef.current = false

        setStatus('error')
        let errorMsg = 'Failed to connect Google Calendar. Please try again.'
        if (err instanceof Error) {
          errorMsg = err.message
          if (err.message.includes('401') || err.message.includes('Not authenticated')) {
            errorMsg = 'Session expired. Please log in again and retry.'
          } else if (err.message.includes('503') || err.message.includes('not configured')) {
            errorMsg = 'Google Calendar integration is not available. Please contact support.'
          }
        }
        setErrorMessage(errorMsg)
      }
    }

    handleCallback()
  }, [searchParams, router])

  if (status === 'loading') {
    return (
      <main className="min-h-screen bg-gradient-to-b from-teal-50 to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-stone-700 animate-pulse" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zM9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm-8 4H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/>
              </svg>
            </div>
            <CardTitle>Connecting Google Calendar...</CardTitle>
            <CardDescription>
              Verifying your Google authorization, please wait
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
          </CardContent>
        </Card>
      </main>
    )
  }

  if (status === 'error') {
    return (
      <main className="min-h-screen bg-gradient-to-b from-teal-50 to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <CardTitle className="text-red-600">Connection Failed</CardTitle>
            <CardDescription>
              {errorMessage}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <Link href="/dashboard">
              <Button className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-700 hover:to-teal-600">
                Return to Dashboard
              </Button>
            </Link>
            <Link href="/employer/login">
              <Button variant="outline" className="w-full">
                Log In Again
              </Button>
            </Link>
          </CardContent>
        </Card>
      </main>
    )
  }

  // Success state
  return (
    <main className="min-h-screen bg-gradient-to-b from-teal-50 to-white flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-teal-50 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <CardTitle className="text-teal-600">Google Calendar Connected!</CardTitle>
          <CardDescription>
            You can now schedule interviews with candidates directly from Pathway
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <p className="text-sm text-stone-600 mb-4">
            Redirecting to your dashboard...
          </p>
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-teal-600"></div>
          </div>
        </CardContent>
      </Card>
    </main>
  )
}

function LoadingFallback() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-teal-50 to-white flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-stone-700 animate-pulse" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zM9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm-8 4H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/>
            </svg>
          </div>
          <CardTitle>Loading...</CardTitle>
        </CardHeader>
        <CardContent className="flex justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
        </CardContent>
      </Card>
    </main>
  )
}

export default function EmployerGoogleCallbackPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <EmployerGoogleCallbackContent />
    </Suspense>
  )
}
