'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { CustomSelect } from '@/components/ui/custom-select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { calendarApi, MeetingDetails, ApiError } from '@/lib/api'

interface ScheduleMeetingProps {
  candidateId: string
  defaultTitle?: string
  defaultDescription?: string
  defaultAttendees?: string[]
  onScheduled?: (meeting: MeetingDetails) => void
  trigger?: React.ReactNode
}

export function ScheduleMeeting({
  candidateId,
  defaultTitle = '',
  defaultDescription = '',
  defaultAttendees = [],
  onScheduled,
  trigger,
}: ScheduleMeetingProps) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<MeetingDetails | null>(null)

  const [title, setTitle] = useState(defaultTitle)
  const [description, setDescription] = useState(defaultDescription)
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [duration, setDuration] = useState('30')
  const [attendees, setAttendees] = useState(defaultAttendees.join(', '))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      setError('Please enter a meeting title')
      return
    }

    if (!date || !time) {
      setError('Please select a date and time')
      return
    }

    const attendeeList = attendees
      .split(',')
      .map(email => email.trim())
      .filter(email => email.length > 0)

    if (attendeeList.length === 0) {
      setError('Please add at least one attendee email')
      return
    }

    // Validate emails
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    const invalidEmails = attendeeList.filter(email => !emailRegex.test(email))
    if (invalidEmails.length > 0) {
      setError(`Invalid email(s): ${invalidEmails.join(', ')}`)
      return
    }

    try {
      setLoading(true)
      setError(null)

      const startTime = new Date(`${date}T${time}`)

      // Check if date is in the past
      if (startTime < new Date()) {
        setError('Cannot schedule a meeting in the past')
        setLoading(false)
        return
      }

      const meeting = await calendarApi.createMeeting(candidateId, {
        title: title.trim(),
        description: description.trim(),
        startTime,
        durationMinutes: parseInt(duration),
        attendeeEmails: attendeeList,
      })

      setSuccess(meeting)
      onScheduled?.(meeting)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to schedule meeting. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setOpen(false)
    // Reset form after dialog closes
    setTimeout(() => {
      setSuccess(null)
      setError(null)
      setTitle(defaultTitle)
      setDescription(defaultDescription)
      setDate('')
      setTime('')
      setDuration('30')
      setAttendees(defaultAttendees.join(', '))
    }, 200)
  }

  // Get min date (today)
  const today = new Date().toISOString().split('T')[0]

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Schedule Meeting
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        {success ? (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-green-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Meeting Scheduled!
              </DialogTitle>
              <DialogDescription>
                Calendar invites have been sent to all attendees.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="bg-green-50 rounded-lg p-4 space-y-3">
                <div>
                  <p className="text-sm font-medium text-green-800">Google Meet Link:</p>
                  {success.meetLink ? (
                    <a
                      href={success.meetLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-indigo-600 hover:underline break-all"
                    >
                      {success.meetLink}
                    </a>
                  ) : (
                    <p className="text-sm text-stone-600">No video link generated</p>
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium text-green-800">Calendar Event:</p>
                  <a
                    href={success.calendarLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-indigo-600 hover:underline"
                  >
                    View in Google Calendar
                  </a>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button onClick={handleClose}>
                Done
              </Button>
            </DialogFooter>
          </>
        ) : (
          <form onSubmit={handleSubmit}>
            <DialogHeader>
              <DialogTitle>Schedule a Meeting</DialogTitle>
              <DialogDescription>
                Create a calendar event with a Google Meet link.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              {error && (
                <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="title">Meeting Title *</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Interview with Acme Corp"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="date">Date *</Label>
                  <Input
                    id="date"
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    min={today}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="time">Time *</Label>
                  <Input
                    id="time"
                    type="time"
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="duration">Duration</Label>
                <CustomSelect
                  value={duration}
                  onChange={(v) => setDuration(v)}
                  options={[
                    { value: '15', label: '15 minutes' },
                    { value: '30', label: '30 minutes' },
                    { value: '45', label: '45 minutes' },
                    { value: '60', label: '1 hour' },
                    { value: '90', label: '1.5 hours' },
                    { value: '120', label: '2 hours' },
                  ]}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="attendees">Attendee Emails *</Label>
                <Input
                  id="attendees"
                  value={attendees}
                  onChange={(e) => setAttendees(e.target.value)}
                  placeholder="recruiter@company.com, hiring@company.com"
                />
                <p className="text-xs text-stone-500">Separate multiple emails with commas</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Meeting agenda, topics to discuss..."
                  rows={3}
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Scheduling...
                  </>
                ) : (
                  'Schedule Meeting'
                )}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}
