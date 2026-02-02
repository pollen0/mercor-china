'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'

interface PermissionCheckProps {
  onPermissionGranted: () => void
}

type PermissionStatus = 'checking' | 'granted' | 'denied' | 'prompt'

export function PermissionCheck({ onPermissionGranted }: PermissionCheckProps) {
  const [cameraStatus, setCameraStatus] = useState<PermissionStatus>('checking')
  const [micStatus, setMicStatus] = useState<PermissionStatus>('checking')
  const [error, setError] = useState<string | null>(null)
  const [isRequesting, setIsRequesting] = useState(false)

  const checkPermissions = useCallback(async () => {
    try {
      // Check camera permission
      const cameraPermission = await navigator.permissions.query({ name: 'camera' as PermissionName })
      setCameraStatus(cameraPermission.state as PermissionStatus)

      // Check microphone permission
      const micPermission = await navigator.permissions.query({ name: 'microphone' as PermissionName })
      setMicStatus(micPermission.state as PermissionStatus)

      // Listen for permission changes
      cameraPermission.onchange = () => setCameraStatus(cameraPermission.state as PermissionStatus)
      micPermission.onchange = () => setMicStatus(micPermission.state as PermissionStatus)

      // If both granted, proceed
      if (cameraPermission.state === 'granted' && micPermission.state === 'granted') {
        onPermissionGranted()
      }
    } catch {
      // Fallback for browsers that don't support permissions API
      setCameraStatus('prompt')
      setMicStatus('prompt')
    }
  }, [onPermissionGranted])

  useEffect(() => {
    checkPermissions()
  }, [checkPermissions])

  const requestPermissions = async () => {
    setIsRequesting(true)
    setError(null)

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      })

      // Stop all tracks immediately after getting permission
      stream.getTracks().forEach(track => track.stop())

      setCameraStatus('granted')
      setMicStatus('granted')
      onPermissionGranted()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'

      if (errorMessage.includes('NotAllowedError') || errorMessage.includes('Permission denied')) {
        setError('Camera and microphone access was denied. Please allow access in your browser settings.')
        setCameraStatus('denied')
        setMicStatus('denied')
      } else if (errorMessage.includes('NotFoundError')) {
        setError('No camera or microphone found. Please connect a camera and microphone.')
      } else {
        setError(`Failed to access camera/microphone: ${errorMessage}`)
      }
    } finally {
      setIsRequesting(false)
    }
  }

  const getStatusIcon = (status: PermissionStatus) => {
    switch (status) {
      case 'granted':
        return (
          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )
      case 'denied':
        return (
          <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        )
      default:
        return (
          <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
            <div className="w-2 h-2 bg-gray-400 rounded-full" />
          </div>
        )
    }
  }

  const allGranted = cameraStatus === 'granted' && micStatus === 'granted'

  return (
    <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
      <div className="text-center mb-8">
        <div className="mx-auto w-16 h-16 bg-gradient-to-br from-teal-100 to-teal-50 rounded-full flex items-center justify-center mb-6">
          <svg className="w-8 h-8 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </div>
        <h1 className="text-xl font-semibold text-gray-900 mb-2">Permission Required</h1>
        <p className="text-gray-500 text-sm">
          We need access to your camera and microphone to record your interview responses.
        </p>
      </div>

      <div className="space-y-3 mb-6">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <span className="font-medium text-gray-900">Camera</span>
              <p className="text-xs text-gray-500">For video recording</p>
            </div>
          </div>
          {getStatusIcon(cameraStatus)}
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center shadow-sm">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <div>
              <span className="font-medium text-gray-900">Microphone</span>
              <p className="text-xs text-gray-500">For audio recording</p>
            </div>
          </div>
          {getStatusIcon(micStatus)}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl mb-6">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Skip option for testing when no device is found */}
      {error && error.includes('not found') && (
        <Button
          variant="outline"
          className="w-full h-12 mb-3 text-amber-600 border-amber-300 hover:bg-amber-50"
          onClick={onPermissionGranted}
        >
          <span className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Skip for Testing (No Camera Mode)
          </span>
        </Button>
      )}

      {!allGranted && (
        <Button
          className="w-full h-12 bg-teal-600 hover:bg-teal-700 text-base font-medium"
          onClick={requestPermissions}
          disabled={isRequesting}
        >
          {isRequesting ? (
            <span className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Requesting Access...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Grant Access
            </span>
          )}
        </Button>
      )}

      {allGranted && (
        <Button
          className="w-full h-12 bg-teal-600 hover:bg-teal-700 text-base font-medium"
          onClick={onPermissionGranted}
        >
          <span className="flex items-center gap-2">
            Continue
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </span>
        </Button>
      )}

      <p className="text-xs text-gray-400 text-center mt-4">
        Your privacy is important. Videos are only used for interview evaluation.
      </p>
    </div>
  )
}
