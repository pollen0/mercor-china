'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
import { Button } from '@/components/ui/button'

interface VideoRecorderProps {
  onRecordingComplete: (blob: Blob) => void
  maxDuration?: number // in seconds
  onError?: (error: string) => void
}

type RecordingState = 'idle' | 'recording' | 'paused' | 'stopped' | 'preview'

export function VideoRecorder({
  onRecordingComplete,
  maxDuration = 120, // 2 minutes default
  onError,
}: VideoRecorderProps) {
  const [state, setState] = useState<RecordingState>('idle')
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null)
  const [recordedUrl, setRecordedUrl] = useState<string | null>(null)
  const [duration, setDuration] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  const videoRef = useRef<HTMLVideoElement>(null)
  const previewRef = useRef<HTMLVideoElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)

  // Initialize camera with mobile-optimized settings
  const initCamera = useCallback(async () => {
    try {
      setIsLoading(true)

      // Detect mobile device
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)

      // Mobile-optimized constraints
      const constraints = {
        video: {
          width: { ideal: isMobile ? 640 : 1280 },
          height: { ideal: isMobile ? 480 : 720 },
          facingMode: 'user',
          // Mobile browsers work better with lower framerates
          frameRate: { ideal: isMobile ? 24 : 30 },
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      }

      const stream = await navigator.mediaDevices.getUserMedia(constraints)

      streamRef.current = stream

      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }

      setIsLoading(false)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to access camera'
      onError?.(message)
      setIsLoading(false)
    }
  }, [onError])

  useEffect(() => {
    initCamera()

    return () => {
      // Cleanup
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (recordedUrl) {
        URL.revokeObjectURL(recordedUrl)
      }
    }
  }, [initCamera, recordedUrl])

  const startRecording = useCallback(() => {
    if (!streamRef.current) {
      onError?.('Camera not initialized')
      return
    }

    chunksRef.current = []

    const options = { mimeType: 'video/webm;codecs=vp9,opus' }
    let mediaRecorder: MediaRecorder

    try {
      mediaRecorder = new MediaRecorder(streamRef.current, options)
    } catch {
      // Fallback to default options
      mediaRecorder = new MediaRecorder(streamRef.current)
    }

    mediaRecorderRef.current = mediaRecorder

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data)
      }
    }

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' })
      setRecordedBlob(blob)
      const url = URL.createObjectURL(blob)
      setRecordedUrl(url)
      setState('preview')
    }

    mediaRecorder.start(1000) // Collect data every second
    setState('recording')
    setDuration(0)

    // Start timer
    timerRef.current = setInterval(() => {
      setDuration(prev => {
        const newDuration = prev + 1
        if (newDuration >= maxDuration) {
          stopRecording()
        }
        return newDuration
      })
    }, 1000)
  }, [maxDuration, onError])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    if (timerRef.current) {
      clearInterval(timerRef.current)
    }
    setState('stopped')
  }, [])

  const retryRecording = useCallback(() => {
    if (recordedUrl) {
      URL.revokeObjectURL(recordedUrl)
    }
    setRecordedBlob(null)
    setRecordedUrl(null)
    setDuration(0)
    setState('idle')

    // Reinitialize camera if needed
    if (!streamRef.current || !streamRef.current.active) {
      initCamera()
    }
  }, [recordedUrl, initCamera])

  const confirmRecording = useCallback(() => {
    if (recordedBlob) {
      onRecordingComplete(recordedBlob)
    }
  }, [recordedBlob, onRecordingComplete])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const remainingTime = maxDuration - duration

  return (
    <div className="space-y-4">
      {/* Video display */}
      <div className="relative aspect-video bg-slate-900 rounded-xl overflow-hidden">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-900">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-slate-700 border-t-emerald-500 rounded-full animate-spin mx-auto mb-3" />
              <div className="text-slate-400 text-sm">Loading camera...</div>
            </div>
          </div>
        )}

        {/* Live preview */}
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className={`w-full h-full object-cover ${state === 'preview' ? 'hidden' : ''}`}
        />

        {/* Recorded preview */}
        {state === 'preview' && recordedUrl && (
          <video
            ref={previewRef}
            src={recordedUrl}
            controls
            className="w-full h-full object-cover"
          />
        )}

        {/* Recording indicator */}
        {state === 'recording' && (
          <div className="absolute top-4 left-4 flex items-center gap-2 bg-red-600 text-white px-3 py-1.5 rounded-full shadow-lg">
            <div className="w-2.5 h-2.5 bg-white rounded-full animate-pulse" />
            <span className="text-sm font-semibold">REC</span>
          </div>
        )}

        {/* Timer */}
        {(state === 'recording' || state === 'preview') && (
          <div className="absolute top-4 right-4 bg-black/60 backdrop-blur-sm text-white px-3 py-1.5 rounded-full">
            <span className="text-sm font-mono">
              {formatTime(duration)} / {formatTime(maxDuration)}
            </span>
          </div>
        )}

        {/* Time warning */}
        {state === 'recording' && remainingTime <= 30 && remainingTime > 0 && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-amber-500 text-black px-4 py-2 rounded-full shadow-lg">
            <span className="text-sm font-semibold">{remainingTime}s remaining</span>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row justify-center gap-3">
        {state === 'idle' && (
          <Button
            size="lg"
            onClick={startRecording}
            disabled={isLoading}
            className="bg-red-600 hover:bg-red-700 min-h-[52px] text-base font-medium px-8"
          >
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
            </svg>
            Start Recording
          </Button>
        )}

        {state === 'recording' && (
          <Button
            size="lg"
            onClick={stopRecording}
            variant="destructive"
            className="min-h-[52px] text-base font-medium px-8"
          >
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
            Stop Recording
          </Button>
        )}

        {state === 'preview' && (
          <>
            <Button
              size="lg"
              variant="outline"
              onClick={retryRecording}
              className="min-h-[52px] text-base font-medium px-6 border-slate-600 text-slate-200 hover:bg-slate-700 hover:text-white bg-slate-800"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Re-record
            </Button>
            <Button
              size="lg"
              onClick={confirmRecording}
              className="bg-emerald-600 hover:bg-emerald-700 min-h-[52px] text-base font-medium px-6"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Use This Recording
            </Button>
          </>
        )}
      </div>

      {/* Instructions */}
      {state === 'idle' && (
        <p className="text-center text-sm text-slate-400">
          Click &quot;Start Recording&quot; when you&apos;re ready. You have up to {formatTime(maxDuration)} to answer.
        </p>
      )}

      {state === 'preview' && (
        <p className="text-center text-sm text-slate-400">
          Review your recording. Click &quot;Use This Recording&quot; to submit, or &quot;Re-record&quot; to try again.
        </p>
      )}
    </div>
  )
}
