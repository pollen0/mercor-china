'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { DashboardNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import { AvailabilityGrid } from '@/components/scheduling'
import {
  employerApi,
  teamMemberApi,
  type Employer,
  type TeamMember,
  type AvailabilitySlot,
  type AvailabilityException,
  type TimeSlot,
} from '@/lib/api'

const TIMEZONES = [
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'America/Denver', label: 'Mountain Time (MT)' },
  { value: 'America/Chicago', label: 'Central Time (CT)' },
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'America/Anchorage', label: 'Alaska Time (AKT)' },
  { value: 'Pacific/Honolulu', label: 'Hawaii Time (HT)' },
  { value: 'Europe/London', label: 'GMT/UTC' },
  { value: 'Europe/Paris', label: 'Central European Time (CET)' },
  { value: 'Asia/Tokyo', label: 'Japan Standard Time (JST)' },
  { value: 'Asia/Shanghai', label: 'China Standard Time (CST)' },
]

interface GridSlot {
  dayOfWeek: number
  startTime: string
  endTime: string
}

export default function AvailabilitySettingsPage() {
  const router = useRouter()
  const params = useParams()
  const teamMemberId = params.id as string

  const [employer, setEmployer] = useState<Employer | null>(null)
  const [teamMember, setTeamMember] = useState<TeamMember | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Availability state
  const [timezone, setTimezone] = useState('America/Los_Angeles')
  const [slots, setSlots] = useState<GridSlot[]>([])
  const [exceptions, setExceptions] = useState<AvailabilityException[]>([])

  // Exception form state
  const [showExceptionModal, setShowExceptionModal] = useState(false)
  const [exceptionForm, setExceptionForm] = useState({
    date: '',
    isUnavailable: true,
    startTime: '',
    endTime: '',
    reason: '',
  })

  // Preview state
  const [previewSlots, setPreviewSlots] = useState<TimeSlot[]>([])
  const [isLoadingPreview, setIsLoadingPreview] = useState(false)

  // Load data
  useEffect(() => {
    const loadData = async () => {
      try {
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/employer/login')
          return
        }

        const [employerData, memberData, availabilityData] = await Promise.all([
          employerApi.getMe(),
          teamMemberApi.get(teamMemberId),
          teamMemberApi.getAvailability(teamMemberId),
        ])

        setEmployer(employerData)
        setTeamMember(memberData)
        setTimezone(availabilityData.timezone || 'America/Los_Angeles')
        setSlots(availabilityData.slots.map(s => ({
          dayOfWeek: s.dayOfWeek,
          startTime: s.startTime,
          endTime: s.endTime,
        })))
        setExceptions(availabilityData.exceptions)
      } catch (err) {
        console.error('Failed to load data:', err)
        if (err instanceof Error && err.message.includes('401')) {
          localStorage.removeItem('employer_token')
          router.push('/employer/login')
        } else {
          setError('Failed to load availability settings')
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [router, teamMemberId])

  // Load preview slots when availability changes
  useEffect(() => {
    const loadPreview = async () => {
      if (!teamMemberId || slots.length === 0) {
        setPreviewSlots([])
        return
      }

      setIsLoadingPreview(true)
      try {
        const today = new Date()
        const nextWeek = new Date(today)
        nextWeek.setDate(today.getDate() + 7)

        const result = await teamMemberApi.getAvailableSlots(teamMemberId, {
          startDate: today.toISOString().split('T')[0],
          endDate: nextWeek.toISOString().split('T')[0],
          durationMinutes: 30,
        })
        setPreviewSlots(result.slots.slice(0, 10))
      } catch (err) {
        console.error('Failed to load preview:', err)
      } finally {
        setIsLoadingPreview(false)
      }
    }

    // Debounce the preview load
    const timeout = setTimeout(loadPreview, 500)
    return () => clearTimeout(timeout)
  }, [teamMemberId, slots])

  const handleLogout = () => {
    localStorage.removeItem('employer_token')
    localStorage.removeItem('employer')
    router.push('/employer/login')
  }

  const handleSaveAvailability = async () => {
    setError(null)
    setSuccessMessage(null)
    setIsSaving(true)

    try {
      await teamMemberApi.setAvailability(teamMemberId, {
        slots: slots,
        timezone: timezone,
      })
      setSuccessMessage('Availability saved successfully')
    } catch (err) {
      console.error('Failed to save availability:', err)
      setError(err instanceof Error ? err.message : 'Failed to save availability')
    } finally {
      setIsSaving(false)
    }
  }

  const handleAddException = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    try {
      const newException = await teamMemberApi.addException(teamMemberId, {
        date: exceptionForm.date,
        isUnavailable: exceptionForm.isUnavailable,
        startTime: exceptionForm.startTime || undefined,
        endTime: exceptionForm.endTime || undefined,
        reason: exceptionForm.reason || undefined,
      })
      setExceptions([...exceptions, newException])
      setShowExceptionModal(false)
      setExceptionForm({
        date: '',
        isUnavailable: true,
        startTime: '',
        endTime: '',
        reason: '',
      })
    } catch (err) {
      console.error('Failed to add exception:', err)
      setError(err instanceof Error ? err.message : 'Failed to add exception')
    }
  }

  const handleDeleteException = async (exceptionId: string) => {
    if (!confirm('Are you sure you want to delete this exception?')) return

    try {
      await teamMemberApi.deleteException(teamMemberId, exceptionId)
      setExceptions(exceptions.filter(e => e.id !== exceptionId))
    } catch (err) {
      console.error('Failed to delete exception:', err)
    }
  }

  // Format preview slot time
  const formatPreviewSlot = (slot: TimeSlot): string => {
    const start = new Date(slot.start)
    return start.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  }

  // Format exception date
  const formatExceptionDate = (dateStr: string): string => {
    const date = new Date(dateStr + 'T00:00:00')
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
  }

  // Get upcoming exceptions (future dates only)
  const upcomingExceptions = useMemo(() => {
    const today = new Date().toISOString().split('T')[0]
    return exceptions
      .filter(e => e.date >= today)
      .sort((a, b) => a.date.localeCompare(b.date))
  }, [exceptions])

  if (isLoading) {
    return (
      <PageWrapper className="flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-stone-200 border-t-stone-600 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-stone-500 text-sm">Loading availability...</p>
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      <DashboardNavbar companyName={employer?.companyName} onLogout={handleLogout} />

      <Container className="py-8 pt-24">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-2 mb-2 text-sm">
              <Link
                href="/employer/dashboard/team"
                className="text-stone-500 hover:text-stone-700"
              >
                Team
              </Link>
              <span className="text-stone-300">/</span>
              <span className="text-stone-700">{teamMember?.name}</span>
            </div>
            <h1 className="text-2xl font-semibold text-stone-900">Availability Settings</h1>
            <p className="text-stone-500">Set recurring weekly availability and manage exceptions</p>
          </div>
          <Button onClick={handleSaveAvailability} disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>

        {/* Success/Error messages */}
        {successMessage && (
          <div className="mb-6 p-3 bg-teal-50 text-teal-700 rounded-lg flex items-center justify-between text-sm">
            <span>{successMessage}</span>
            <button onClick={() => setSuccessMessage(null)} className="text-teal-500 hover:text-teal-700">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main availability grid */}
          <div className="lg:col-span-2 space-y-6">
            {/* Timezone selector */}
            <Card>
              <CardHeader>
                <CardTitle>Timezone</CardTitle>
              </CardHeader>
              <CardContent>
                <select
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-stone-900/10 focus:border-stone-300"
                >
                  {TIMEZONES.map(tz => (
                    <option key={tz.value} value={tz.value}>
                      {tz.label}
                    </option>
                  ))}
                </select>
                <p className="text-sm text-stone-500 mt-2">
                  All times will be displayed in this timezone
                </p>
              </CardContent>
            </Card>

            {/* Weekly availability grid */}
            <Card>
              <CardHeader>
                <CardTitle>Weekly Availability</CardTitle>
              </CardHeader>
              <CardContent>
                <AvailabilityGrid
                  slots={slots}
                  onChange={setSlots}
                  timezone={timezone}
                />
              </CardContent>
            </Card>

            {/* Exceptions */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Exceptions</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowExceptionModal(true)}
                >
                  Add Exception
                </Button>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-stone-500 mb-4">
                  Block specific dates or add extra availability outside your regular schedule
                </p>

                {upcomingExceptions.length === 0 ? (
                  <div className="text-center py-6 text-stone-500">
                    <p>No upcoming exceptions</p>
                    <p className="text-sm text-stone-400">Add exceptions for holidays, PTO, or other schedule changes</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {upcomingExceptions.map(exception => (
                      <div
                        key={exception.id}
                        className={`flex items-center justify-between p-3 rounded-lg border ${
                          exception.isUnavailable
                            ? 'bg-red-50 border-red-100'
                            : 'bg-teal-50 border-teal-100'
                        }`}
                      >
                        <div>
                          <div className="flex items-center gap-2">
                            <span className={`text-sm font-medium ${
                              exception.isUnavailable ? 'text-red-700' : 'text-teal-700'
                            }`}>
                              {exception.isUnavailable ? 'Blocked' : 'Available'}
                            </span>
                            <span className="text-stone-700 font-medium">
                              {formatExceptionDate(exception.date)}
                            </span>
                          </div>
                          {exception.startTime && exception.endTime && (
                            <span className="text-sm text-stone-500">
                              {exception.startTime} - {exception.endTime}
                            </span>
                          )}
                          {exception.reason && (
                            <p className="text-sm text-stone-500 mt-1">{exception.reason}</p>
                          )}
                        </div>
                        <button
                          onClick={() => handleDeleteException(exception.id)}
                          className="text-stone-400 hover:text-red-600 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - Preview */}
          <div className="space-y-6">
            {/* Team member info */}
            <Card>
              <CardHeader>
                <CardTitle>Team Member</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-stone-100 text-stone-600 flex items-center justify-center font-medium">
                    {teamMember?.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-stone-900">{teamMember?.name}</p>
                    <p className="text-sm text-stone-500">{teamMember?.email}</p>
                    <p className="text-xs text-stone-400 capitalize">{teamMember?.role.replace('_', ' ')}</p>
                  </div>
                </div>
                {teamMember?.googleCalendarConnected && (
                  <div className="mt-3 flex items-center gap-2 text-sm text-teal-600">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 16H6c-.55 0-1-.45-1-1V8h14v10c0 .55-.45 1-1 1z" />
                    </svg>
                    Google Calendar connected
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Interview limits */}
            <Card>
              <CardHeader>
                <CardTitle>Interview Limits</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-stone-500">Daily limit</span>
                    <span className="font-medium text-stone-900">{teamMember?.maxInterviewsPerDay} interviews</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-stone-500">Weekly limit</span>
                    <span className="font-medium text-stone-900">{teamMember?.maxInterviewsPerWeek} interviews</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Preview */}
            <Card>
              <CardHeader>
                <CardTitle>Preview Available Slots</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-stone-500 mb-3">
                  Next 7 days (30-min slots)
                </p>

                {isLoadingPreview ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="w-5 h-5 border-2 border-stone-200 border-t-stone-600 rounded-full animate-spin" />
                  </div>
                ) : previewSlots.length === 0 ? (
                  <div className="text-center py-4 text-stone-500 text-sm">
                    No available slots in the next 7 days
                  </div>
                ) : (
                  <div className="space-y-1">
                    {previewSlots.map((slot, i) => (
                      <div
                        key={i}
                        className="px-3 py-2 bg-stone-50 rounded text-sm text-stone-700"
                      >
                        {formatPreviewSlot(slot)}
                      </div>
                    ))}
                    {previewSlots.length === 10 && (
                      <p className="text-xs text-stone-400 text-center mt-2">
                        Showing first 10 slots
                      </p>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </Container>

      {/* Add Exception Modal */}
      {showExceptionModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
            <form onSubmit={handleAddException}>
              <div className="p-6 border-b">
                <h2 className="text-xl font-semibold">Add Exception</h2>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <Label htmlFor="exceptionDate">Date *</Label>
                  <Input
                    id="exceptionDate"
                    type="date"
                    value={exceptionForm.date}
                    onChange={e => setExceptionForm({ ...exceptionForm, date: e.target.value })}
                    required
                    min={new Date().toISOString().split('T')[0]}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label>Type *</Label>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <button
                      type="button"
                      onClick={() => setExceptionForm({ ...exceptionForm, isUnavailable: true })}
                      className={`p-3 rounded-lg border text-center transition-colors ${
                        exceptionForm.isUnavailable
                          ? 'border-red-300 bg-red-50 text-red-700'
                          : 'border-stone-200 hover:border-stone-300'
                      }`}
                    >
                      <div className="font-medium">Blocked</div>
                      <div className="text-xs text-stone-500">Not available</div>
                    </button>
                    <button
                      type="button"
                      onClick={() => setExceptionForm({ ...exceptionForm, isUnavailable: false })}
                      className={`p-3 rounded-lg border text-center transition-colors ${
                        !exceptionForm.isUnavailable
                          ? 'border-teal-300 bg-teal-50 text-teal-700'
                          : 'border-stone-200 hover:border-stone-300'
                      }`}
                    >
                      <div className="font-medium">Available</div>
                      <div className="text-xs text-stone-500">Extra availability</div>
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="startTime">Start Time (optional)</Label>
                    <Input
                      id="startTime"
                      type="time"
                      value={exceptionForm.startTime}
                      onChange={e => setExceptionForm({ ...exceptionForm, startTime: e.target.value })}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="endTime">End Time (optional)</Label>
                    <Input
                      id="endTime"
                      type="time"
                      value={exceptionForm.endTime}
                      onChange={e => setExceptionForm({ ...exceptionForm, endTime: e.target.value })}
                      className="mt-1"
                    />
                  </div>
                </div>
                <p className="text-xs text-stone-500 -mt-2">
                  Leave times empty to apply to the entire day
                </p>

                <div>
                  <Label htmlFor="reason">Reason (optional)</Label>
                  <Input
                    id="reason"
                    value={exceptionForm.reason}
                    onChange={e => setExceptionForm({ ...exceptionForm, reason: e.target.value })}
                    placeholder="e.g., PTO, Holiday, Doctor appointment"
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="p-6 border-t flex justify-end gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowExceptionModal(false)}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  Add Exception
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </PageWrapper>
  )
}
