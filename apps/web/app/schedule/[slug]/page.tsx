'use client'

import { useState, useEffect, useMemo } from 'react'
import { useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { SlotPicker } from '@/components/scheduling'
import {
  schedulingLinkApi,
  type PublicSchedulingLink,
} from '@/lib/api'

interface TimeSlot {
  start: string
  end: string
}

type BookingState = 'loading' | 'select_slot' | 'enter_details' | 'confirming' | 'confirmed' | 'error'

export default function PublicSchedulePage() {
  const params = useParams()
  const slug = params.slug as string

  const [state, setState] = useState<BookingState>('loading')
  const [linkInfo, setLinkInfo] = useState<PublicSchedulingLink | null>(null)
  const [slots, setSlots] = useState<TimeSlot[]>([])
  const [timezone, setTimezone] = useState('America/Los_Angeles')
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Booking form
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    notes: '',
  })

  // Confirmation data
  const [confirmation, setConfirmation] = useState<{
    scheduledAt: string
    durationMinutes: number
    interviewerName?: string
    googleMeetLink?: string
    calendarLink?: string
  } | null>(null)

  // Detect user's timezone
  useEffect(() => {
    try {
      const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
      if (userTimezone) {
        setTimezone(userTimezone)
      }
    } catch (e) {
      console.log('Could not detect timezone')
    }
  }, [])

  // Load scheduling link data
  useEffect(() => {
    const loadData = async () => {
      try {
        const result = await schedulingLinkApi.getPublic(slug)
        setLinkInfo(result.link)
        setSlots(result.slots)
        setTimezone(result.timezone || timezone)
        setState('select_slot')
      } catch (err) {
        console.error('Failed to load scheduling link:', err)
        setError('This scheduling link is no longer available or has expired.')
        setState('error')
      }
    }

    if (slug) {
      loadData()
    }
  }, [slug])

  const handleSelectSlot = (slotStart: string) => {
    setSelectedSlot(slotStart)
  }

  const handleContinueToDetails = () => {
    if (selectedSlot) {
      setState('enter_details')
    }
  }

  const handleBackToSlots = () => {
    setState('select_slot')
  }

  const handleSubmitBooking = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedSlot || !formData.name || !formData.email) {
      setError('Please fill in all required fields')
      return
    }

    setState('confirming')
    setError(null)

    try {
      const result = await schedulingLinkApi.book(slug, {
        slotStart: selectedSlot,
        candidateName: formData.name,
        candidateEmail: formData.email,
        candidatePhone: formData.phone || undefined,
        candidateNotes: formData.notes || undefined,
        timezone: timezone,
      })

      if (result.success) {
        setConfirmation({
          scheduledAt: result.scheduledAt!,
          durationMinutes: result.durationMinutes || linkInfo?.durationMinutes || 30,
          interviewerName: result.interviewerName,
          googleMeetLink: result.googleMeetLink,
          calendarLink: result.calendarLink,
        })
        setState('confirmed')
      } else {
        setError(result.error || 'Failed to book the slot. Please try again.')
        setState('enter_details')
      }
    } catch (err) {
      console.error('Failed to book:', err)
      setError(err instanceof Error ? err.message : 'Failed to book the slot. Please try again.')
      setState('enter_details')
    }
  }

  // Format time for display
  const formatDateTime = (dateStr: string): string => {
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      timeZoneName: 'short',
    })
  }

  const formatTime = (dateStr: string): string => {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  }

  // Loading state
  if (state === 'loading') {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-stone-200 border-t-stone-600 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-stone-500 text-sm">Loading...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (state === 'error') {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="py-12 text-center">
            <div className="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-stone-900 mb-2">Link Not Available</h2>
            <p className="text-stone-500 text-sm">{error}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Confirmed state
  if (state === 'confirmed' && confirmation) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center p-4">
        <Card className="max-w-lg w-full">
          <CardContent className="py-8">
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-teal-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-stone-900 mb-2">Interview Confirmed</h2>
              <p className="text-stone-500 text-sm">
                A confirmation email has been sent to {formData.email}
              </p>
            </div>

            <div className="bg-stone-50 rounded-lg p-4 mb-6">
              <h3 className="font-medium text-stone-900 mb-3 text-sm">Interview Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-stone-500">Interview</span>
                  <span className="font-medium text-stone-900">{linkInfo?.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-stone-500">Date & Time</span>
                  <span className="font-medium text-stone-900">{formatDateTime(confirmation.scheduledAt)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-stone-500">Duration</span>
                  <span className="font-medium text-stone-900">{confirmation.durationMinutes} minutes</span>
                </div>
                {confirmation.interviewerName && (
                  <div className="flex justify-between">
                    <span className="text-stone-500">Interviewer</span>
                    <span className="font-medium text-stone-900">{confirmation.interviewerName}</span>
                  </div>
                )}
                {linkInfo?.companyName && (
                  <div className="flex justify-between">
                    <span className="text-stone-500">Company</span>
                    <span className="font-medium text-stone-900">{linkInfo.companyName}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Action buttons */}
            <div className="space-y-3">
              {confirmation.googleMeetLink && (
                <a
                  href={confirmation.googleMeetLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-stone-900 text-white rounded-lg text-sm font-medium hover:bg-stone-800 transition-colors"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
                  </svg>
                  Join with Google Meet
                </a>
              )}
              {confirmation.calendarLink && (
                <a
                  href={confirmation.calendarLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full py-2.5 px-4 border border-stone-200 text-stone-700 rounded-lg text-sm font-medium hover:bg-stone-50 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Add to Calendar
                </a>
              )}
            </div>

            <p className="text-xs text-stone-400 text-center mt-6">
              You can close this window. Check your email for complete details.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <div className="bg-white border-b border-stone-100">
        <div className="max-w-2xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            {linkInfo?.companyLogo && (
              <img
                src={linkInfo.companyLogo}
                alt={linkInfo.companyName}
                className="w-10 h-10 rounded-lg object-cover"
              />
            )}
            <div>
              <h1 className="text-lg font-semibold text-stone-900">{linkInfo?.companyName}</h1>
              {linkInfo?.jobTitle && (
                <p className="text-sm text-stone-500">{linkInfo.jobTitle}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">{linkInfo?.name}</CardTitle>
            {linkInfo?.description && (
              <p className="text-stone-500 text-sm">{linkInfo.description}</p>
            )}
            <div className="flex items-center gap-4 text-sm text-stone-500 mt-2">
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {linkInfo?.durationMinutes} minutes
              </span>
            </div>
          </CardHeader>

          <CardContent>
            {/* Select slot */}
            {state === 'select_slot' && (
              <div className="space-y-6">
                {error && (
                  <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                    {error}
                  </div>
                )}

                <SlotPicker
                  slots={slots}
                  selectedSlot={selectedSlot}
                  onSelect={handleSelectSlot}
                  timezone={timezone}
                  durationMinutes={linkInfo?.durationMinutes || 30}
                />

                <div className="flex justify-end">
                  <Button
                    onClick={handleContinueToDetails}
                    disabled={!selectedSlot}
                  >
                    Continue
                  </Button>
                </div>
              </div>
            )}

            {/* Enter details */}
            {state === 'enter_details' && (
              <form onSubmit={handleSubmitBooking} className="space-y-6">
                {error && (
                  <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                    {error}
                  </div>
                )}

                {/* Selected slot summary */}
                <div className="bg-stone-50 border border-stone-100 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-stone-500">Selected time</p>
                      <p className="font-medium text-stone-900">
                        {selectedSlot && formatDateTime(selectedSlot)}
                      </p>
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleBackToSlots}
                    >
                      Change
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Your Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={e => setFormData({ ...formData, name: e.target.value })}
                      placeholder="John Doe"
                      required
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="email">Email Address *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={e => setFormData({ ...formData, email: e.target.value })}
                      placeholder="john@example.com"
                      required
                      className="mt-1"
                    />
                    <p className="text-xs text-stone-400 mt-1">
                      Confirmation and meeting details will be sent here
                    </p>
                  </div>

                  <div>
                    <Label htmlFor="phone">Phone Number (optional)</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={e => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="+1 (555) 123-4567"
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="notes">Additional Notes (optional)</Label>
                    <textarea
                      id="notes"
                      value={formData.notes}
                      onChange={e => setFormData({ ...formData, notes: e.target.value })}
                      placeholder="Anything you'd like us to know..."
                      rows={3}
                      className="mt-1 w-full px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-stone-900/10 focus:border-stone-300"
                    />
                  </div>
                </div>

                <div className="flex justify-between">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleBackToSlots}
                  >
                    Back
                  </Button>
                  <Button type="submit">
                    Confirm Booking
                  </Button>
                </div>
              </form>
            )}

            {/* Confirming */}
            {state === 'confirming' && (
              <div className="py-12 text-center">
                <div className="w-8 h-8 border-2 border-stone-200 border-t-stone-600 rounded-full animate-spin mx-auto mb-3" />
                <p className="text-stone-600 text-sm">Confirming your booking...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-xs text-stone-400">
            Powered by{' '}
            <a
              href="/"
              className="text-stone-600 hover:text-stone-900 font-medium"
              target="_blank"
              rel="noopener noreferrer"
            >
              Pathway
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
