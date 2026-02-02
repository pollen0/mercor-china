'use client'

import { Suspense, useEffect, useState, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { candidateApi } from '@/lib/api'

function GitHubCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [errorMessage, setErrorMessage] = useState('')
  const [githubUsername, setGithubUsername] = useState('')

  // Ref to prevent double execution (React Strict Mode runs effects twice)
  // OAuth codes can only be used ONCE, so we must guard against this
  const isProcessingRef = useRef(false)

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')
      const errorDescription = searchParams.get('error_description')

      // CRITICAL: Prevent double execution - OAuth codes can only be used once
      // React Strict Mode runs effects twice, which would cause the second call to fail
      if (isProcessingRef.current) {
        console.log('[GitHub OAuth] Already processing, skipping duplicate call')
        return
      }

      // Also check sessionStorage for the specific code being processed
      // This handles edge cases like fast page refreshes
      const processingCode = sessionStorage.getItem('github_oauth_processing')
      if (processingCode === code) {
        console.log('[GitHub OAuth] This code is already being processed')
        return
      }

      // Check if user is logged in
      const token = localStorage.getItem('candidate_token')
      if (!token) {
        setStatus('error')
        setErrorMessage('You must be logged in to connect GitHub. Please log in and try again.')
        return
      }

      // Check for GitHub errors
      if (error) {
        setStatus('error')
        setErrorMessage(errorDescription || 'GitHub authorization was cancelled or failed')
        return
      }

      if (!code) {
        setStatus('error')
        setErrorMessage('No authorization code received. Please try again.')
        return
      }

      // Validate CSRF state token
      const savedState = sessionStorage.getItem('github_oauth_state')
      if (state && savedState && state !== savedState) {
        setStatus('error')
        setErrorMessage('Security validation failed. Please try again.')
        return
      }

      // Mark as processing BEFORE clearing state and making API call
      isProcessingRef.current = true
      sessionStorage.setItem('github_oauth_processing', code)

      // Clear the saved state
      sessionStorage.removeItem('github_oauth_state')

      try {
        console.log('[GitHub OAuth] Exchanging code for token...')

        // Exchange code for token and connect GitHub with timeout
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => reject(new Error('Request timed out. Please try again.')), 30000)
        })

        const result = await Promise.race([
          candidateApi.connectGitHub(code, state || undefined),
          timeoutPromise
        ])

        console.log('[GitHub OAuth] Successfully connected GitHub')
        setGithubUsername(result.githubUsername)
        setStatus('success')

        // Clear the processing marker on success
        sessionStorage.removeItem('github_oauth_processing')

        // Redirect after a short delay to the dashboard profile tab
        setTimeout(() => {
          router.push('/candidate/dashboard?tab=profile&github=connected')
        }, 2000)
      } catch (err) {
        console.error('[GitHub OAuth] Connection error:', err)

        // Clear the processing marker on error so user can retry
        sessionStorage.removeItem('github_oauth_processing')
        isProcessingRef.current = false

        setStatus('error')
        let errorMsg = 'Failed to connect GitHub. Please try again.'
        if (err instanceof Error) {
          errorMsg = err.message
          // Handle specific error cases
          if (err.message.includes('401') || err.message.includes('Not authenticated')) {
            errorMsg = 'Session expired. Please log in again and retry.'
          } else if (err.message.includes('503') || err.message.includes('not configured')) {
            errorMsg = 'GitHub integration is not available. Please contact support.'
          } else if (err.message.includes('409') || err.message.includes('already connected')) {
            errorMsg = 'This GitHub account is already connected to another user.'
          } else if (
            err.message.includes('Bad credentials') ||
            err.message.includes('bad_verification_code') ||
            err.message.includes('already been used') ||
            err.message.includes('expired')
          ) {
            errorMsg = 'Authorization code expired or already used. Please try connecting again from your profile.'
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
              <svg className="w-8 h-8 text-stone-800 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
              </svg>
            </div>
            <CardTitle>Connecting GitHub...</CardTitle>
            <CardDescription>
              Verifying your GitHub authorization, please wait
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
            <Link href="/candidate/dashboard?tab=profile">
              <Button className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-700 hover:to-teal-600">
                Return to Profile
              </Button>
            </Link>
            <Link href="/candidate/dashboard?tab=interviews">
              <Button variant="outline" className="w-full">
                Go to Interviews
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
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <CardTitle className="text-green-600">GitHub Connected!</CardTitle>
          <CardDescription>
            Successfully connected as <span className="font-medium text-stone-900">@{githubUsername}</span>
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <p className="text-sm text-stone-600 mb-4">
            Your GitHub profile and repositories have been synced. Redirecting to your dashboard...
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
            <svg className="w-8 h-8 text-stone-800 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
              <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
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

export default function GitHubCallbackPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <GitHubCallbackContent />
    </Suspense>
  )
}
