'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { scheduledInterviewApi, type ScheduledInterview, type ScheduledInterviewStatus } from '@/lib/api'

const STATUS_CONFIG: Record<ScheduledInterviewStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'error' | 'outline' }> = {
  pending: { label: 'Pending', variant: 'warning' },
  confirmed: { label: 'Confirmed', variant: 'success' },
  completed: { label: 'Completed', variant: 'default' },
  cancelled: { label: 'Cancelled', variant: 'error' },
  no_show: { label: 'No Show', variant: 'error' },
  rescheduled: { label: 'Rescheduled', variant: 'outline' },
}

const INTERVIEW_TYPE_LABELS: Record<string, string> = {
  phone_screen: 'Phone Screen',
  technical: 'Technical',
  behavioral: 'Behavioral',
  culture_fit: 'Culture Fit',
  final: 'Final Round',
  other: 'Interview',
}

export default function ScheduledInterviewsPage() {
  const router = useRouter()
  const [interviews, setInterviews] = useState<ScheduledInterview[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'upcoming' | 'past' | 'all'>('upcoming')
  const [cancellingId, setCancellingId] = useState<string | null>(null)

  // Reschedule modal state
  const [showRescheduleModal, setShowRescheduleModal] = useState(false)
  const [rescheduleInterview, setRescheduleInterview] = useState<ScheduledInterview | null>(null)
  const [rescheduleDate, setRescheduleDate] = useState('')
  const [rescheduleTime, setRescheduleTime] = useState('')
  const [rescheduleReason, setRescheduleReason] = useState('')
  const [rescheduling, setRescheduling] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('employer_token')
    if (!token) {
      router.push('/employer/login')
      return
    }
    loadInterviews()
  }, [router])

  const loadInterviews = async () => {
    try {
      setLoading(true)
      const { interviews: data } = await scheduledInterviewApi.list()
      setInterviews(data)
      setError(null)
    } catch (err) {
      console.error('Failed to load interviews:', err)
      setError('Failed to load scheduled interviews')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (interview: ScheduledInterview) => {
    if (!confirm(`Are you sure you want to cancel the interview with ${interview.candidateName}?`)) {
      return
    }

    setCancellingId(interview.id)
    try {
      await scheduledInterviewApi.cancel(interview.id, true)
      await loadInterviews()
    } catch (err) {
      console.error('Failed to cancel interview:', err)
      alert('Failed to cancel interview. Please try again.')
    } finally {
      setCancellingId(null)
    }
  }

  const openRescheduleModal = (interview: ScheduledInterview) => {
    setRescheduleInterview(interview)
    // Pre-fill with current date/time
    const date = new Date(interview.scheduledAt)
    setRescheduleDate(date.toISOString().split('T')[0])
    setRescheduleTime(date.toTimeString().slice(0, 5))
    setRescheduleReason('')
    setShowRescheduleModal(true)
  }

  const handleReschedule = async () => {
    if (!rescheduleInterview || !rescheduleDate || !rescheduleTime) return

    setRescheduling(true)
    try {
      const newDateTime = new Date(`${rescheduleDate}T${rescheduleTime}`)
      await scheduledInterviewApi.reschedule(rescheduleInterview.id, {
        scheduledAt: newDateTime,
        reason: rescheduleReason || undefined,
      })
      setShowRescheduleModal(false)
      setRescheduleInterview(null)
      await loadInterviews()
    } catch (err) {
      console.error('Failed to reschedule interview:', err)
      alert('Failed to reschedule interview. Please try again.')
    } finally {
      setRescheduling(false)
    }
  }

  // Filter interviews based on active tab
  const now = new Date()
  const filteredInterviews = interviews.filter(interview => {
    const interviewDate = new Date(interview.scheduledAt)
    if (activeTab === 'upcoming') {
      return interviewDate >= now && !['cancelled', 'completed', 'no_show'].includes(interview.status)
    } else if (activeTab === 'past') {
      return interviewDate < now || ['cancelled', 'completed', 'no_show'].includes(interview.status)
    }
    return true
  }).sort((a, b) => {
    // Sort upcoming by soonest first, past by most recent first
    const dateA = new Date(a.scheduledAt).getTime()
    const dateB = new Date(b.scheduledAt).getTime()
    return activeTab === 'upcoming' ? dateA - dateB : dateB - dateA
  })

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  }

  const getTimeUntil = (dateStr: string) => {
    const date = new Date(dateStr)
    const diff = date.getTime() - now.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)

    if (diff < 0) return 'Past'
    if (days > 0) return `In ${days} day${days > 1 ? 's' : ''}`
    if (hours > 0) return `In ${hours} hour${hours > 1 ? 's' : ''}`
    const minutes = Math.floor(diff / (1000 * 60))
    return `In ${minutes} minute${minutes > 1 ? 's' : ''}`
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-stone-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-stone-200 border-t-stone-600 rounded-full animate-spin" />
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-stone-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-2 text-sm text-stone-500 mb-2">
              <Link href="/employer/dashboard" className="hover:text-stone-700">Dashboard</Link>
              <span>/</span>
              <span className="text-stone-700">Scheduled Interviews</span>
            </div>
            <h1 className="text-2xl font-semibold text-stone-900">Scheduled Interviews</h1>
            <p className="text-stone-500 mt-1">Manage your upcoming and past interviews</p>
          </div>
          <Link href="/employer/dashboard/scheduling-links">
            <Button variant="outline">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              Scheduling Links
            </Button>
          </Link>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1 p-1 bg-stone-100 rounded-lg w-fit mb-6">
          {(['upcoming', 'past', 'all'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                activeTab === tab
                  ? 'bg-white text-stone-900 shadow-sm'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {tab === 'upcoming' && (
                <span className="ml-2 px-2 py-0.5 bg-teal-100 text-teal-700 text-xs rounded-full">
                  {interviews.filter(i => new Date(i.scheduledAt) >= now && !['cancelled', 'completed', 'no_show'].includes(i.status)).length}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Interview List */}
        {filteredInterviews.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <svg className="w-12 h-12 text-stone-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p className="text-stone-500">
                {activeTab === 'upcoming' ? 'No upcoming interviews' : activeTab === 'past' ? 'No past interviews' : 'No interviews scheduled'}
              </p>
              <p className="text-sm text-stone-400 mt-1">
                When candidates book through your scheduling links, they&apos;ll appear here
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredInterviews.map(interview => {
              const statusConfig = STATUS_CONFIG[interview.status]
              const isUpcoming = new Date(interview.scheduledAt) >= now && !['cancelled', 'completed', 'no_show'].includes(interview.status)

              return (
                <Card key={interview.id} className={interview.status === 'cancelled' ? 'opacity-60' : ''}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex gap-4">
                        {/* Date/Time Block */}
                        <div className="text-center p-3 bg-stone-50 rounded-lg min-w-[100px]">
                          <div className="text-2xl font-bold text-stone-900">
                            {new Date(interview.scheduledAt).getDate()}
                          </div>
                          <div className="text-sm text-stone-500">
                            {new Date(interview.scheduledAt).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                          </div>
                          <div className="text-sm font-medium text-stone-700 mt-1">
                            {formatTime(interview.scheduledAt)}
                          </div>
                        </div>

                        {/* Interview Details */}
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-semibold text-stone-900">{interview.candidateName || 'Unknown Candidate'}</h3>
                            <Badge variant={statusConfig.variant}>{statusConfig.label}</Badge>
                            {isUpcoming && (
                              <span className="text-xs text-teal-600 font-medium">{getTimeUntil(interview.scheduledAt)}</span>
                            )}
                          </div>
                          <p className="text-sm text-stone-500 mb-1">{interview.candidateEmail}</p>
                          <div className="flex items-center gap-4 text-sm text-stone-600">
                            <span className="flex items-center gap-1">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              {interview.durationMinutes} min
                            </span>
                            <span className="flex items-center gap-1">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                              </svg>
                              {INTERVIEW_TYPE_LABELS[interview.interviewType] || interview.interviewType}
                            </span>
                            {interview.jobTitle && (
                              <span className="flex items-center gap-1">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                </svg>
                                {interview.jobTitle}
                              </span>
                            )}
                          </div>
                          {interview.employerNotes && (
                            <p className="text-sm text-stone-500 mt-2 italic">Note: {interview.employerNotes}</p>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2">
                        {interview.googleMeetLink && isUpcoming && (
                          <a
                            href={interview.googleMeetLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors text-sm font-medium"
                          >
                            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                            </svg>
                            Join Meeting
                          </a>
                        )}
                        {isUpcoming && interview.status !== 'cancelled' && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => openRescheduleModal(interview)}
                            >
                              Reschedule
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-red-600 hover:bg-red-50 hover:border-red-200"
                              onClick={() => handleCancel(interview)}
                              disabled={cancellingId === interview.id}
                            >
                              {cancellingId === interview.id ? 'Cancelling...' : 'Cancel'}
                            </Button>
                          </>
                        )}
                        {interview.calendarLink && (
                          <a
                            href={interview.calendarLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 text-stone-400 hover:text-stone-600 hover:bg-stone-100 rounded-lg transition-colors"
                            title="View in Calendar"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                          </a>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>

      {/* Reschedule Modal */}
      {showRescheduleModal && rescheduleInterview && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Reschedule Interview</CardTitle>
              <CardDescription>
                Reschedule interview with {rescheduleInterview.candidateName}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">New Date</label>
                <input
                  type="date"
                  value={rescheduleDate}
                  onChange={(e) => setRescheduleDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">New Time</label>
                <input
                  type="time"
                  value={rescheduleTime}
                  onChange={(e) => setRescheduleTime(e.target.value)}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">Reason (optional)</label>
                <textarea
                  value={rescheduleReason}
                  onChange={(e) => setRescheduleReason(e.target.value)}
                  placeholder="Let the candidate know why..."
                  rows={3}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setShowRescheduleModal(false)
                    setRescheduleInterview(null)
                  }}
                  disabled={rescheduling}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 bg-teal-600 hover:bg-teal-700"
                  onClick={handleReschedule}
                  disabled={rescheduling || !rescheduleDate || !rescheduleTime}
                >
                  {rescheduling ? 'Rescheduling...' : 'Reschedule'}
                </Button>
              </div>
              <p className="text-xs text-stone-500 text-center">
                The candidate will receive an updated calendar invite
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </main>
  )
}
