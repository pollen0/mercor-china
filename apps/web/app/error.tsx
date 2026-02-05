'use client'

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error)
  }, [error])

  return (
    <main className="min-h-screen bg-white flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="mb-6">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
            <svg
              className="w-8 h-8 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        </div>
        <h2 className="text-2xl font-semibold text-stone-900 mb-4">
          Something went wrong
        </h2>
        <p className="text-stone-500 mb-8">
          We encountered an unexpected error. Please try again, or contact support
          if the problem persists.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={reset}
            className="inline-flex items-center justify-center px-6 py-3 bg-stone-900 text-white rounded-full hover:bg-stone-800 transition-colors"
          >
            Try again
          </button>
          <a
            href="/"
            className="inline-flex items-center justify-center px-6 py-3 border border-stone-200 text-stone-700 rounded-full hover:bg-stone-50 transition-colors"
          >
            Go home
          </a>
        </div>
        {process.env.NODE_ENV === 'development' && error.message && (
          <div className="mt-8 p-4 bg-stone-100 rounded-lg text-left">
            <p className="text-xs font-mono text-stone-600 break-all">
              {error.message}
            </p>
          </div>
        )}
      </div>
    </main>
  )
}
