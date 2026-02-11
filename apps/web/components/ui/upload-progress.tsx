'use client'

import { useEffect, useState } from 'react'

interface UploadProgressProps {
  progress: number // 0-100
  isUploading: boolean
  fileName?: string
}

export function UploadProgress({ progress, isUploading, fileName }: UploadProgressProps) {
  const [displayProgress, setDisplayProgress] = useState(0)

  // Smooth animation for progress bar
  useEffect(() => {
    if (!isUploading) {
      setDisplayProgress(0)
      return
    }

    // Animate towards target progress
    const timer = setInterval(() => {
      setDisplayProgress(current => {
        const diff = progress - current
        if (Math.abs(diff) < 0.5) return progress
        return current + diff * 0.15 // Smooth easing
      })
    }, 16) // ~60fps

    return () => clearInterval(timer)
  }, [progress, isUploading])

  if (!isUploading) return null

  return (
    <div className="mt-4 space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-stone-600 truncate max-w-[200px]">
          {fileName ? `Uploading ${fileName}...` : 'Uploading...'}
        </span>
        <span className="text-stone-500 font-medium">{Math.round(displayProgress)}%</span>
      </div>
      <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-teal-500 to-teal-400 rounded-full transition-all duration-150 ease-out"
          style={{ width: `${displayProgress}%` }}
        />
      </div>
      {progress < 100 && (
        <p className="text-xs text-stone-400">
          {progress < 30 ? 'Uploading file...' : progress < 70 ? 'Processing document...' : 'Almost done...'}
        </p>
      )}
    </div>
  )
}
