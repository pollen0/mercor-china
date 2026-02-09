'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { DashboardNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import {
  employerApi,
  teamMemberApi,
  type Employer,
  type TeamMember,
  type TeamMemberRole,
} from '@/lib/api'

const ROLES: { value: TeamMemberRole; label: string; description: string }[] = [
  { value: 'admin', label: 'Admin', description: 'Full access to all settings' },
  { value: 'recruiter', label: 'Recruiter', description: 'Manage candidates and scheduling' },
  { value: 'hiring_manager', label: 'Hiring Manager', description: 'Review candidates and make decisions' },
  { value: 'interviewer', label: 'Interviewer', description: 'Conduct interviews only' },
]

export default function TeamManagementPage() {
  const router = useRouter()
  const [employer, setEmployer] = useState<Employer | null>(null)
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingMember, setEditingMember] = useState<TeamMember | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'interviewer' as TeamMemberRole,
    maxInterviewsPerDay: 4,
    maxInterviewsPerWeek: 15,
  })
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load data
  useEffect(() => {
    const loadData = async () => {
      try {
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/employer/login')
          return
        }

        const [employerData, teamData] = await Promise.all([
          employerApi.getMe(),
          teamMemberApi.list(true),
        ])

        setEmployer(employerData)
        setTeamMembers(teamData.teamMembers)
      } catch (err) {
        console.error('Failed to load data:', err)
        if (err instanceof Error && err.message.includes('401')) {
          localStorage.removeItem('employer_token')
          router.push('/employer/login')
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('employer_token')
    localStorage.removeItem('employer')
    router.push('/employer/login')
  }

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      role: 'interviewer',
      maxInterviewsPerDay: 4,
      maxInterviewsPerWeek: 15,
    })
    setError(null)
  }

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSaving(true)

    try {
      const newMember = await teamMemberApi.create({
        name: formData.name,
        email: formData.email,
        role: formData.role,
        maxInterviewsPerDay: formData.maxInterviewsPerDay,
        maxInterviewsPerWeek: formData.maxInterviewsPerWeek,
      })

      setTeamMembers([newMember, ...teamMembers])
      setShowAddModal(false)
      resetForm()
    } catch (err) {
      console.error('Failed to add team member:', err)
      setError(err instanceof Error ? err.message : 'Failed to add team member')
    } finally {
      setIsSaving(false)
    }
  }

  const handleUpdateMember = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingMember) return

    setError(null)
    setIsSaving(true)

    try {
      const updated = await teamMemberApi.update(editingMember.id, {
        name: formData.name,
        role: formData.role,
        maxInterviewsPerDay: formData.maxInterviewsPerDay,
        maxInterviewsPerWeek: formData.maxInterviewsPerWeek,
      })

      setTeamMembers(teamMembers.map(m => m.id === updated.id ? updated : m))
      setEditingMember(null)
      resetForm()
    } catch (err) {
      console.error('Failed to update team member:', err)
      setError(err instanceof Error ? err.message : 'Failed to update team member')
    } finally {
      setIsSaving(false)
    }
  }

  const handleToggleActive = async (member: TeamMember) => {
    try {
      const updated = await teamMemberApi.update(member.id, {
        isActive: !member.isActive,
      })
      setTeamMembers(teamMembers.map(m => m.id === updated.id ? updated : m))
    } catch (err) {
      console.error('Failed to toggle member status:', err)
    }
  }

  const handleDeleteMember = async (memberId: string) => {
    if (!confirm('Are you sure you want to remove this team member?')) return

    try {
      await teamMemberApi.delete(memberId)
      setTeamMembers(teamMembers.filter(m => m.id !== memberId))
    } catch (err) {
      console.error('Failed to delete team member:', err)
    }
  }

  const startEdit = (member: TeamMember) => {
    setFormData({
      name: member.name,
      email: member.email,
      role: member.role,
      maxInterviewsPerDay: member.maxInterviewsPerDay,
      maxInterviewsPerWeek: member.maxInterviewsPerWeek,
    })
    setEditingMember(member)
  }

  const handleConnectCalendar = async (memberId: string) => {
    try {
      const { url } = await teamMemberApi.getCalendarConnectUrl(memberId)
      // Store member ID in session for callback
      sessionStorage.setItem('calendar_connect_member_id', memberId)
      window.location.href = url
    } catch (err) {
      console.error('Failed to get calendar URL:', err)
      alert('Failed to connect Google Calendar. Please try again.')
    }
  }

  const handleDisconnectCalendar = async (memberId: string) => {
    if (!confirm('Are you sure you want to disconnect Google Calendar?')) return

    try {
      await teamMemberApi.disconnectCalendar(memberId)
      setTeamMembers(teamMembers.map(m =>
        m.id === memberId
          ? { ...m, googleCalendarConnected: false, googleCalendarConnectedAt: undefined }
          : m
      ))
    } catch (err) {
      console.error('Failed to disconnect calendar:', err)
    }
  }

  if (isLoading) {
    return (
      <PageWrapper className="flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-stone-200 border-t-stone-600 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-stone-500 text-sm">Loading team...</p>
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
            <h1 className="text-2xl font-semibold text-stone-900">Team Management</h1>
            <p className="text-stone-500">Manage your interview team and their availability</p>
          </div>
          <Button onClick={() => { resetForm(); setShowAddModal(true) }}>
            Add Team Member
          </Button>
        </div>

        {/* Team Members List */}
        <div className="space-y-4">
          {teamMembers.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-stone-500 mb-4">No team members yet</p>
                <Button onClick={() => { resetForm(); setShowAddModal(true) }}>
                  Add Your First Team Member
                </Button>
              </CardContent>
            </Card>
          ) : (
            teamMembers.map(member => (
              <Card key={member.id} className={!member.isActive ? 'opacity-60' : ''}>
                <CardContent className="py-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-center gap-3 sm:gap-4">
                      {/* Avatar */}
                      <div className="w-10 h-10 rounded-full bg-stone-100 text-stone-600 flex items-center justify-center font-medium flex-shrink-0">
                        {member.name.charAt(0).toUpperCase()}
                      </div>

                      {/* Info */}
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-medium text-stone-900">{member.name}</h3>
                          <span className={`px-2 py-0.5 text-xs rounded-full ${
                            member.isActive ? 'bg-teal-50 text-teal-700' : 'bg-stone-100 text-stone-500'
                          }`}>
                            {member.isActive ? 'Active' : 'Inactive'}
                          </span>
                          <span className="px-2 py-0.5 text-xs bg-stone-100 text-stone-600 rounded-full capitalize">
                            {member.role.replace('_', ' ')}
                          </span>
                        </div>
                        <p className="text-sm text-stone-500">{member.email}</p>
                        <div className="flex items-center gap-3 mt-1 text-xs text-stone-400">
                          <span>Max {member.maxInterviewsPerDay}/day</span>
                          <span>Max {member.maxInterviewsPerWeek}/week</span>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-wrap items-center gap-2 sm:flex-nowrap">
                      {/* Calendar status */}
                      {member.googleCalendarConnected ? (
                        <button
                          onClick={() => handleDisconnectCalendar(member.id)}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-teal-700 bg-teal-50 rounded-lg hover:bg-teal-100 transition-colors"
                          title="Calendar connected - click to disconnect"
                        >
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 16H6c-.55 0-1-.45-1-1V8h14v10c0 .55-.45 1-1 1z" />
                          </svg>
                          Connected
                        </button>
                      ) : (
                        <button
                          onClick={() => handleConnectCalendar(member.id)}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-stone-600 bg-stone-100 rounded-lg hover:bg-stone-200 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 16H6c-.55 0-1-.45-1-1V8h14v10c0 .55-.45 1-1 1z" />
                          </svg>
                          Connect Calendar
                        </button>
                      )}

                      {/* Availability link */}
                      <Link href={`/employer/dashboard/team/${member.id}/availability`}>
                        <Button variant="outline" size="sm">
                          Availability
                        </Button>
                      </Link>

                      {/* Edit button */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => startEdit(member)}
                      >
                        Edit
                      </Button>

                      {/* Toggle active */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleActive(member)}
                      >
                        {member.isActive ? 'Deactivate' : 'Activate'}
                      </Button>

                      {/* Delete */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteMember(member.id)}
                        className="text-red-600 hover:bg-red-50"
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </Container>

      {/* Add/Edit Modal */}
      {(showAddModal || editingMember) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
            <form onSubmit={editingMember ? handleUpdateMember : handleAddMember}>
              <div className="p-6 border-b">
                <h2 className="text-xl font-semibold">
                  {editingMember ? 'Edit Team Member' : 'Add Team Member'}
                </h2>
              </div>

              <div className="p-6 space-y-4">
                {error && (
                  <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                    {error}
                  </div>
                )}

                <div>
                  <Label htmlFor="name">Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                    required
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                    required
                    disabled={!!editingMember}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label>Role *</Label>
                  <div className="grid gap-2 mt-2">
                    {ROLES.map(role => (
                      <button
                        key={role.value}
                        type="button"
                        onClick={() => setFormData({ ...formData, role: role.value })}
                        className={`p-3 rounded-lg border text-left transition-colors ${
                          formData.role === role.value
                            ? 'border-stone-900 bg-stone-50'
                            : 'border-stone-200 hover:border-stone-300'
                        }`}
                      >
                        <div className="font-medium text-stone-900">{role.label}</div>
                        <div className="text-sm text-stone-500">{role.description}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="maxDay">Max Interviews/Day</Label>
                    <Input
                      id="maxDay"
                      type="number"
                      min={1}
                      max={20}
                      value={formData.maxInterviewsPerDay}
                      onChange={e => setFormData({ ...formData, maxInterviewsPerDay: parseInt(e.target.value) || 4 })}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="maxWeek">Max Interviews/Week</Label>
                    <Input
                      id="maxWeek"
                      type="number"
                      min={1}
                      max={50}
                      value={formData.maxInterviewsPerWeek}
                      onChange={e => setFormData({ ...formData, maxInterviewsPerWeek: parseInt(e.target.value) || 15 })}
                      className="mt-1"
                    />
                  </div>
                </div>
              </div>

              <div className="p-6 border-t flex justify-end gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowAddModal(false)
                    setEditingMember(null)
                    resetForm()
                  }}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isSaving}>
                  {isSaving ? 'Saving...' : editingMember ? 'Save Changes' : 'Add Member'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </PageWrapper>
  )
}
