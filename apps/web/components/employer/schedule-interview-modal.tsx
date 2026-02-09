'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CustomSelect } from '@/components/ui/custom-select'
import { scheduledInterviewApi, InterviewType, ApiError, Job } from '@/lib/api'

interface ScheduleInterviewModalProps {
  candidateId: string
  candidateName: string
  candidateEmail: string
  jobs?: Job[]
  onClose: () => void
  onSuccess?: (interview: { googleMeetLink?: string; calendarLink?: string }) => void
}

const INTERVIEW_TYPES: { value: InterviewType; label: string }[] = [
  { value: 'phone_screen', label: 'Phone Screen' },
  { value: 'technical', label: 'Technical Interview' },
  { value: 'behavioral', label: 'Behavioral Interview' },
  { value: 'culture_fit', label: 'Culture Fit' },
  { value: 'final', label: 'Final Interview' },
  { value: 'other', label: 'Other' },
]

const DURATION_OPTIONS = [
  { value: 15, label: '15 minutes' },
  { value: 30, label: '30 minutes' },
  { value: 45, label: '45 minutes' },
  { value: 60, label: '1 hour' },
  { value: 90, label: '1.5 hours' },
  { value: 120, label: '2 hours' },
]

const TIMEZONE_OPTIONS = [
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'America/Denver', label: 'Mountain Time (MT)' },
  { value: 'America/Chicago', label: 'Central Time (CT)' },
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'UTC', label: 'UTC' },
]

export function ScheduleInterviewModal({
  candidateId,
  candidateName,
  candidateEmail,
  jobs = [],
  onClose,
  onSuccess,
}: ScheduleInterviewModalProps) {
  const [interviewType, setInterviewType] = useState<InterviewType>('technical')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [duration, setDuration] = useState(30)
  const [timezone, setTimezone] = useState('America/Los_Angeles')
  const [jobId, setJobId] = useState<string>('')
  const [additionalAttendees, setAdditionalAttendees] = useState('')
  const [employerNotes, setEmployerNotes] = useState('')

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<{
    googleMeetLink?: string
    calendarLink?: string
  } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validate required fields
    if (!date || !time) {
      setError('Please select a date and time')
      return
    }

    // Parse date and time
    const scheduledAt = new Date(`${date}T${time}`)
    if (isNaN(scheduledAt.getTime())) {
      setError('Invalid date or time')
      return
    }

    // Check if date is in the future
    if (scheduledAt <= new Date()) {
      setError('Please select a future date and time')
      return
    }

    // Parse additional attendees
    const attendees = additionalAttendees
      .split(/[,\n]/)
      .map(email => email.trim())
      .filter(email => email && email.includes('@'))

    setIsSubmitting(true)

    try {
      const result = await scheduledInterviewApi.schedule(candidateId, {
        interviewType,
        title: title || undefined,
        description: description || undefined,
        scheduledAt,
        durationMinutes: duration,
        timezone,
        jobId: jobId || undefined,
        additionalAttendees: attendees.length > 0 ? attendees : undefined,
        employerNotes: employerNotes || undefined,
      })

      setSuccess({
        googleMeetLink: result.googleMeetLink,
        calendarLink: result.calendarLink,
      })

      if (onSuccess) {
        onSuccess({
          googleMeetLink: result.googleMeetLink,
          calendarLink: result.calendarLink,
        })
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to schedule interview. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  // Success state
  if (success) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <CardTitle>Interview Scheduled!</CardTitle>
            <CardDescription>
              Calendar invites have been sent to {candidateName} and all attendees.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {success.googleMeetLink && (
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm font-medium text-blue-900 mb-2">Google Meet Link</p>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={success.googleMeetLink}
                    readOnly
                    className="flex-1 text-sm bg-white border border-blue-200 rounded px-3 py-2"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      navigator.clipboard.writeText(success.googleMeetLink!)
                    }}
                  >
                    Copy
                  </Button>
                </div>
                <a
                  href={success.googleMeetLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline mt-2"
                >
                  Open in new tab
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            )}

            {success.calendarLink && (
              <a
                href={success.calendarLink}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 text-teal-600 hover:underline"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zM9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm-8 4H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/>
                </svg>
                View in Google Calendar
              </a>
            )}

            <Button onClick={onClose} className="w-full" variant="default">
              Done
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Schedule Interview</span>
            <button
              onClick={onClose}
              className="text-stone-400 hover:text-stone-600"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </CardTitle>
          <CardDescription>
            Schedule an interview with {candidateName} ({candidateEmail})
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Interview Type */}
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Interview Type
              </label>
              <CustomSelect
                value={interviewType}
                onChange={(v) => setInterviewType(v as InterviewType)}
                options={INTERVIEW_TYPES}
                placeholder="Select interview type"
              />
            </div>

            {/* Date and Time */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  required
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Time <span className="text-red-500">*</span>
                </label>
                <input
                  type="time"
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>
            </div>

            {/* Duration and Timezone */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Duration
                </label>
                <CustomSelect
                  value={String(duration)}
                  onChange={(v) => setDuration(Number(v))}
                  options={DURATION_OPTIONS.map(o => ({ value: String(o.value), label: o.label }))}
                  placeholder="Select duration"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Timezone
                </label>
                <CustomSelect
                  value={timezone}
                  onChange={(v) => setTimezone(v)}
                  options={TIMEZONE_OPTIONS}
                  placeholder="Select timezone"
                />
              </div>
            </div>

            {/* Job Selection */}
            {jobs.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Related Job (optional)
                </label>
                <CustomSelect
                  value={jobId}
                  onChange={(v) => setJobId(v)}
                  options={[
                    { value: '', label: '-- Select a job --' },
                    ...jobs.map(job => ({ value: job.id, label: job.title })),
                  ]}
                  placeholder="-- Select a job --"
                />
              </div>
            )}

            {/* Custom Title */}
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Custom Title (optional)
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Auto-generated if left blank"
                className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Description / Agenda (optional)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                placeholder="What will be covered in this interview..."
                className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none"
              />
            </div>

            {/* Additional Attendees */}
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Additional Attendees (optional)
              </label>
              <textarea
                value={additionalAttendees}
                onChange={(e) => setAdditionalAttendees(e.target.value)}
                rows={2}
                placeholder="Enter email addresses, separated by commas"
                className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none"
              />
              <p className="text-xs text-stone-500 mt-1">
                Other interviewers who should join. The candidate will be added automatically.
              </p>
            </div>

            {/* Private Notes */}
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Private Notes (optional)
              </label>
              <textarea
                value={employerNotes}
                onChange={(e) => setEmployerNotes(e.target.value)}
                rows={2}
                placeholder="Internal notes (not visible to candidate)"
                className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none"
              />
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={onClose}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="default"
                className="flex-1"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Scheduling...
                  </>
                ) : (
                  'Schedule Interview'
                )}
              </Button>
            </div>

            <p className="text-xs text-stone-500 text-center">
              A Google Meet link will be generated and calendar invites will be sent to all attendees.
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
