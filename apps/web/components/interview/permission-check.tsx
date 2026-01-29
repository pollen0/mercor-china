'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

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
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )
      case 'denied':
        return (
          <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        )
      default:
        return (
          <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
        )
    }
  }

  const allGranted = cameraStatus === 'granted' && micStatus === 'granted'

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="text-center">
        <CardTitle>Permission Check</CardTitle>
        <CardDescription>
          We need access to your camera and microphone to record your interview responses.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span className="font-medium">Camera</span>
            </div>
            {getStatusIcon(cameraStatus)}
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
              <span className="font-medium">Microphone</span>
            </div>
            {getStatusIcon(micStatus)}
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {!allGranted && (
          <Button
            className="w-full min-h-[48px] text-base"
            onClick={requestPermissions}
            disabled={isRequesting}
          >
            {isRequesting ? 'Requesting Access...' : 'Grant Access'}
          </Button>
        )}

        {allGranted && (
          <Button className="w-full min-h-[48px] text-base" onClick={onPermissionGranted}>
            Continue
          </Button>
        )}

        <p className="text-xs text-gray-500 text-center">
          Your privacy is important. Videos are only used for interview evaluation.
        </p>
      </CardContent>
    </Card>
  )
}
