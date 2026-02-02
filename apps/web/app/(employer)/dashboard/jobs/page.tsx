'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

// Redirect to unified dashboard with jobs tab
export default function JobsRedirect() {
  const router = useRouter()

  useEffect(() => {
    router.replace('/dashboard?tab=jobs')
  }, [router])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-gray-200 border-t-teal-600 rounded-full animate-spin mx-auto mb-3" />
        <p className="text-gray-500 text-sm">Redirecting...</p>
      </div>
    </div>
  )
}
