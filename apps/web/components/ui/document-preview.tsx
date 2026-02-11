'use client'

import { useState } from 'react'
import { Button } from './button'
import { Card, CardContent, CardHeader, CardTitle } from './card'

interface DocumentPreviewProps {
  url: string
  fileName?: string
  onClose: () => void
}

export function DocumentPreview({ url, fileName, onClose }: DocumentPreviewProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(false)

  // Determine if it's a PDF
  const isPdf = url.toLowerCase().includes('.pdf') || url.includes('application/pdf')

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl h-[85vh] flex flex-col">
        <CardHeader className="flex-shrink-0 flex flex-row items-center justify-between border-b pb-4">
          <CardTitle className="text-lg truncate pr-4">
            {fileName || 'Document Preview'}
          </CardTitle>
          <div className="flex items-center gap-2">
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-teal-600 hover:text-teal-700 flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Open in new tab
            </a>
            <Button variant="ghost" size="sm" onClick={onClose} className="text-stone-500 hover:text-stone-700">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          </div>
        </CardHeader>
        <CardContent className="flex-1 p-0 overflow-hidden relative">
          {isLoading && !error && (
            <div className="absolute inset-0 flex items-center justify-center bg-stone-50">
              <div className="text-center">
                <div className="w-10 h-10 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin mx-auto mb-3" />
                <p className="text-sm text-stone-500">Loading document...</p>
              </div>
            </div>
          )}

          {error ? (
            <div className="absolute inset-0 flex items-center justify-center bg-stone-50">
              <div className="text-center p-6">
                <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-stone-600 mb-2">Unable to preview this document</p>
                <p className="text-sm text-stone-400 mb-4">The document format may not be supported for inline preview</p>
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-teal-600 hover:text-teal-700"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download document
                </a>
              </div>
            </div>
          ) : (
            <>
              {isPdf ? (
                <iframe
                  src={`${url}#toolbar=1&navpanes=0`}
                  className="w-full h-full border-0"
                  onLoad={() => setIsLoading(false)}
                  onError={() => {
                    setIsLoading(false)
                    setError(true)
                  }}
                  title="Document preview"
                />
              ) : (
                // For non-PDF files (like DOCX), use Google Docs viewer or Office Online
                <iframe
                  src={`https://docs.google.com/viewer?url=${encodeURIComponent(url)}&embedded=true`}
                  className="w-full h-full border-0"
                  onLoad={() => setIsLoading(false)}
                  onError={() => {
                    setIsLoading(false)
                    setError(true)
                  }}
                  title="Document preview"
                />
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
