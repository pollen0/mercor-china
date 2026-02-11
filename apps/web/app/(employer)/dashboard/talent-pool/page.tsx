'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

// Redirect to unified dashboard with talent tab
export default function TalentPoolRedirect() {
  const router = useRouter()

  useEffect(() => {
    router.replace('/dashboard?tab=talent')
  }, [router])

  return (
    <div className="min-h-screen bg-stone-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin mx-auto mb-3" />
        <p className="text-stone-500 text-sm">Redirecting...</p>
      </div>
    </div>
  )
}
