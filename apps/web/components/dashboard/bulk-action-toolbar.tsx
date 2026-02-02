'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'

interface BulkActionToolbarProps {
  selectedCount: number
  onShortlist: () => Promise<void>
  onReject: () => Promise<void>
  onClearSelection: () => void
  isLoading?: boolean
}

export function BulkActionToolbar({
  selectedCount,
  onShortlist,
  onReject,
  onClearSelection,
  isLoading = false
}: BulkActionToolbarProps) {
  const [actionInProgress, setActionInProgress] = useState<'shortlist' | 'reject' | null>(null)

  const handleShortlist = async () => {
    setActionInProgress('shortlist')
    try {
      await onShortlist()
    } finally {
      setActionInProgress(null)
    }
  }

  const handleReject = async () => {
    setActionInProgress('reject')
    try {
      await onReject()
    } finally {
      setActionInProgress(null)
    }
  }

  if (selectedCount === 0) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg p-4 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">
            <span className="font-semibold text-teal-600">{selectedCount}</span> interview{selectedCount > 1 ? 's' : ''} selected
          </span>
          <button
            onClick={onClearSelection}
            className="text-sm text-gray-500 hover:text-gray-700 underline"
          >
            Clear selection
          </button>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={handleReject}
            disabled={isLoading || actionInProgress !== null}
            className="border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300"
          >
            {actionInProgress === 'reject' ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-red-300 border-t-red-600 rounded-full animate-spin" />
                Rejecting...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Reject ({selectedCount})
              </span>
            )}
          </Button>

          <Button
            onClick={handleShortlist}
            disabled={isLoading || actionInProgress !== null}
            className="bg-teal-600 hover:bg-teal-700"
          >
            {actionInProgress === 'shortlist' ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Shortlisting...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Shortlist ({selectedCount})
              </span>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
