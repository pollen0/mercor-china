'use client'

import { useState } from 'react'
import Link from 'next/link'

interface MatchingReadinessAlertProps {
  resumeUploaded: boolean
  githubConnected: boolean
  transcriptUploaded: boolean
  interviewCompleted: boolean
}

export function MatchingReadinessAlert({
  resumeUploaded,
  githubConnected,
  transcriptUploaded,
  interviewCompleted,
}: MatchingReadinessAlertProps) {
  const [isDismissed, setIsDismissed] = useState(false)

  if (isDismissed) return null

  const profileItems = [
    { key: 'resume', label: 'Upload resume', done: resumeUploaded, sectionId: 'resume-section' },
    { key: 'github', label: 'Connect GitHub', done: githubConnected, sectionId: 'github-section' },
    { key: 'transcript', label: 'Upload transcript', done: transcriptUploaded, sectionId: 'transcript-section' },
  ]

  const completedCount = profileItems.filter(i => i.done).length
  const missingItems = profileItems.filter(i => !i.done)
  const allProfileDone = missingItems.length === 0

  // Don't render if everything is done
  if (allProfileDone && interviewCompleted) return null

  const scrollTo = (sectionId: string) => {
    const el = document.getElementById(sectionId)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  // Two-tier messaging
  const isProfileIncomplete = completedCount < 2
  const isProfileReadyNoInterview = !isProfileIncomplete && !interviewCompleted

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <svg className="w-5 h-5 text-amber-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-amber-800">
            {isProfileIncomplete
              ? 'Complete your profile to get matched with companies'
              : 'Boost your matching score'}
          </h3>
          <p className="text-sm text-amber-700 mt-1">
            {isProfileIncomplete
              ? 'Employers can only discover you once your profile has enough information. Add the items below to start getting matched.'
              : 'Your profile is looking good! Complete an interview to rank higher in employer searches.'}
          </p>

          {/* Missing profile items as clickable pills */}
          {missingItems.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {missingItems.map(item => (
                <button
                  key={item.key}
                  onClick={() => scrollTo(item.sectionId)}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700 hover:bg-amber-200 transition-colors"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  {item.label}
                </button>
              ))}
            </div>
          )}

          {/* Interview CTA when profile is ready but no interview */}
          {isProfileReadyNoInterview && (
            <div className="mt-3">
              <Link
                href="/interview/select"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-stone-900 text-white hover:bg-stone-800 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Start Interview
              </Link>
            </div>
          )}
        </div>
        <button
          onClick={() => setIsDismissed(true)}
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
