'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense } from 'react'

function ResumeRedirect() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const isOnboarding = searchParams.get('onboarding') === 'true'
  const githubConnected = searchParams.get('github') === 'connected'

  useEffect(() => {
    // Build redirect URL with any relevant params
    let redirectUrl = '/candidate/dashboard?tab=profile'
    if (isOnboarding) {
      redirectUrl += '&onboarding=true'
    }
    if (githubConnected) {
      redirectUrl += '&github=connected'
    }
    router.replace(redirectUrl)
  }, [router, isOnboarding, githubConnected])

  return (
    <main className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-gray-200 border-t-gray-900 rounded-full animate-spin mx-auto mb-3" />
        <p className="text-gray-400 text-sm">Redirecting to dashboard...</p>
      </div>
    </main>
  )
}

export default function ResumePage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-white flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
      </main>
    }>
      <ResumeRedirect />
    </Suspense>
  )
}
