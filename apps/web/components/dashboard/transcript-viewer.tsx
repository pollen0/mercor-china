'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'

interface TranscriptViewerProps {
  transcript: string
  maxHeight?: string
}

export function TranscriptViewer({ transcript, maxHeight = '200px' }: TranscriptViewerProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isCopied, setIsCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(transcript)
      setIsCopied(true)
      setTimeout(() => setIsCopied(false), 2000)
    } catch {
      // Ignore copy errors
    }
  }

  if (!transcript) {
    return (
      <div className="text-gray-400 text-sm italic">
        No transcript available
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Transcript
        </span>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={handleCopy}
            className="text-gray-500 hover:text-gray-700 h-8"
          >
            {isCopied ? (
              <>
                <svg className="w-4 h-4 mr-1 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Copied
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </>
            )}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-500 hover:text-gray-700 h-8"
          >
            {isExpanded ? (
              <>
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
                Collapse
              </>
            ) : (
              <>
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
                Expand
              </>
            )}
          </Button>
        </div>
      </div>

      <div
        className={`bg-gray-50 rounded-xl p-4 overflow-y-auto transition-all border border-gray-100 ${
          isExpanded ? '' : 'max-h-[200px]'
        }`}
        style={{ maxHeight: isExpanded ? 'none' : maxHeight }}
      >
        <p className="text-gray-700 whitespace-pre-wrap leading-relaxed text-sm">
          {transcript}
        </p>
      </div>

      {!isExpanded && transcript.length > 500 && (
        <button
          onClick={() => setIsExpanded(true)}
          className="text-emerald-600 hover:text-emerald-700 text-sm font-medium"
        >
          Show more...
        </button>
      )}
    </div>
  )
}
