'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { DashboardNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import { InterviewerSelect } from '@/components/scheduling'
import {
  employerApi,
  schedulingLinkApi,
  teamMemberApi,
  type Employer,
  type SchedulingLink,
  type TeamMember,
} from '@/lib/api'

const DURATION_OPTIONS = [
  { value: 15, label: '15 minutes' },
  { value: 30, label: '30 minutes' },
  { value: 45, label: '45 minutes' },
  { value: 60, label: '1 hour' },
  { value: 90, label: '1.5 hours' },
]

export default function SchedulingLinksPage() {
  const router = useRouter()
  const [employer, setEmployer] = useState<Employer | null>(null)
  const [links, setLinks] = useState<SchedulingLink[]>([])
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingLink, setEditingLink] = useState<SchedulingLink | null>(null)
  const [copiedSlug, setCopiedSlug] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    durationMinutes: 30,
    interviewerIds: [] as string[],
    bufferBeforeMinutes: 5,
    bufferAfterMinutes: 5,
    minNoticeHours: 24,
    maxDaysAhead: 14,
  })
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Wizard step (for create modal)
  const [wizardStep, setWizardStep] = useState(1)

  // Load data
  useEffect(() => {
    const loadData = async () => {
      try {
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/employer/login')
          return
        }

        const [employerData, linksData, teamData] = await Promise.all([
          employerApi.getMe(),
          schedulingLinkApi.list(true),
          teamMemberApi.list(true),
        ])

        setEmployer(employerData)
        setLinks(linksData.links)
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
      description: '',
      durationMinutes: 30,
      interviewerIds: [],
      bufferBeforeMinutes: 5,
      bufferAfterMinutes: 5,
      minNoticeHours: 24,
      maxDaysAhead: 14,
    })
    setWizardStep(1)
    setError(null)
  }

  const handleCreateLink = async () => {
    if (formData.interviewerIds.length === 0) {
      setError('Please select at least one interviewer')
      return
    }

    setError(null)
    setIsSaving(true)

    try {
      const newLink = await schedulingLinkApi.create({
        name: formData.name,
        description: formData.description || undefined,
        durationMinutes: formData.durationMinutes,
        interviewerIds: formData.interviewerIds,
        bufferBeforeMinutes: formData.bufferBeforeMinutes,
        bufferAfterMinutes: formData.bufferAfterMinutes,
        minNoticeHours: formData.minNoticeHours,
        maxDaysAhead: formData.maxDaysAhead,
      })

      setLinks([newLink, ...links])
      setShowCreateModal(false)
      resetForm()
    } catch (err) {
      console.error('Failed to create link:', err)
      setError(err instanceof Error ? err.message : 'Failed to create scheduling link')
    } finally {
      setIsSaving(false)
    }
  }

  const handleUpdateLink = async () => {
    if (!editingLink) return
    if (formData.interviewerIds.length === 0) {
      setError('Please select at least one interviewer')
      return
    }

    setError(null)
    setIsSaving(true)

    try {
      const updated = await schedulingLinkApi.update(editingLink.id, {
        name: formData.name,
        description: formData.description || undefined,
        durationMinutes: formData.durationMinutes,
        interviewerIds: formData.interviewerIds,
        bufferBeforeMinutes: formData.bufferBeforeMinutes,
        bufferAfterMinutes: formData.bufferAfterMinutes,
        minNoticeHours: formData.minNoticeHours,
        maxDaysAhead: formData.maxDaysAhead,
      })

      setLinks(links.map(l => l.id === updated.id ? updated : l))
      setEditingLink(null)
      resetForm()
    } catch (err) {
      console.error('Failed to update link:', err)
      setError(err instanceof Error ? err.message : 'Failed to update scheduling link')
    } finally {
      setIsSaving(false)
    }
  }

  const handleToggleActive = async (link: SchedulingLink) => {
    try {
      const updated = await schedulingLinkApi.update(link.id, {
        isActive: !link.isActive,
      })
      setLinks(links.map(l => l.id === updated.id ? updated : l))
    } catch (err) {
      console.error('Failed to toggle link status:', err)
    }
  }

  const handleDeleteLink = async (linkId: string) => {
    if (!confirm('Are you sure you want to delete this scheduling link?')) return

    try {
      await schedulingLinkApi.delete(linkId)
      setLinks(links.filter(l => l.id !== linkId))
    } catch (err) {
      console.error('Failed to delete link:', err)
    }
  }

  const startEdit = (link: SchedulingLink) => {
    setFormData({
      name: link.name,
      description: link.description || '',
      durationMinutes: link.durationMinutes,
      interviewerIds: link.interviewerIds,
      bufferBeforeMinutes: link.bufferBeforeMinutes,
      bufferAfterMinutes: link.bufferAfterMinutes,
      minNoticeHours: link.minNoticeHours,
      maxDaysAhead: link.maxDaysAhead,
    })
    setEditingLink(link)
    setWizardStep(1)
  }

  const copyToClipboard = async (link: SchedulingLink) => {
    const baseUrl = typeof window !== 'undefined' ? window.location.origin : ''
    const url = `${baseUrl}/schedule/${link.slug}`

    try {
      await navigator.clipboard.writeText(url)
      setCopiedSlug(link.slug)
      setTimeout(() => setCopiedSlug(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const formatDate = (dateStr: string): string => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  // Active team members for selection
  const activeTeamMembers = teamMembers.filter(m => m.isActive)

  if (isLoading) {
    return (
      <PageWrapper className="flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-stone-200 border-t-stone-600 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-stone-500 text-sm">Loading scheduling links...</p>
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
            <h1 className="text-2xl font-semibold text-stone-900">Scheduling Links</h1>
            <p className="text-stone-500">Create shareable links for candidates to book interviews</p>
          </div>
          <Button onClick={() => { resetForm(); setShowCreateModal(true) }}>
            Create Link
          </Button>
        </div>

        {/* Links List */}
        <div className="space-y-4">
          {links.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="w-12 h-12 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </div>
                <h3 className="text-base font-medium text-stone-900 mb-1">No scheduling links yet</h3>
                <p className="text-stone-500 text-sm mb-4">
                  Create a scheduling link to let candidates book interviews with your team
                </p>
                <Button onClick={() => { resetForm(); setShowCreateModal(true) }}>
                  Create Your First Link
                </Button>
              </CardContent>
            </Card>
          ) : (
            links.map(link => (
              <Card key={link.id} className={!link.isActive ? 'opacity-60' : ''}>
                <CardContent className="py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-stone-900">{link.name}</h3>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${
                          link.isActive ? 'bg-teal-50 text-teal-700' : 'bg-stone-100 text-stone-500'
                        }`}>
                          {link.isActive ? 'Active' : 'Inactive'}
                        </span>
                      </div>

                      {link.description && (
                        <p className="text-sm text-stone-500 mb-2">{link.description}</p>
                      )}

                      <div className="flex items-center gap-4 text-sm text-stone-500">
                        <span>{link.durationMinutes} min</span>
                        <span>{link.interviewerIds.length} interviewer{link.interviewerIds.length !== 1 ? 's' : ''}</span>
                        <span>Up to {link.maxDaysAhead} days ahead</span>
                      </div>

                      {/* Interviewers */}
                      {link.interviewers && link.interviewers.length > 0 && (
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-xs text-stone-400">Assigned:</span>
                          <div className="flex -space-x-1.5">
                            {link.interviewers.slice(0, 3).map(interviewer => (
                              <div
                                key={interviewer.id}
                                className="w-6 h-6 rounded-full bg-stone-100 text-stone-600 flex items-center justify-center text-xs font-medium border-2 border-white"
                                title={interviewer.name}
                              >
                                {interviewer.name.charAt(0).toUpperCase()}
                              </div>
                            ))}
                            {link.interviewers.length > 3 && (
                              <div className="w-6 h-6 rounded-full bg-stone-100 text-stone-500 flex items-center justify-center text-xs font-medium border-2 border-white">
                                +{link.interviewers.length - 3}
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Stats */}
                      <div className="flex items-center gap-4 mt-3 text-xs text-stone-400">
                        <span>{link.viewCount} views</span>
                        <span>{link.bookingCount} bookings</span>
                        <span>Created {formatDate(link.createdAt)}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(link)}
                        className={copiedSlug === link.slug ? 'bg-teal-50 text-teal-700 border-teal-200' : ''}
                      >
                        {copiedSlug === link.slug ? (
                          <>
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            Copied
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                            </svg>
                            Copy Link
                          </>
                        )}
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => startEdit(link)}
                      >
                        Edit
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleActive(link)}
                      >
                        {link.isActive ? 'Deactivate' : 'Activate'}
                      </Button>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteLink(link.id)}
                        className="text-red-600 hover:bg-red-50"
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </Container>

      {/* Create/Edit Modal */}
      {(showCreateModal || editingLink) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">
                {editingLink ? 'Edit Scheduling Link' : 'Create Scheduling Link'}
              </h2>
              {!editingLink && (
                <div className="flex items-center gap-2 mt-4">
                  {[1, 2, 3].map(step => (
                    <div
                      key={step}
                      className={`flex items-center ${step < 3 ? 'flex-1' : ''}`}
                    >
                      <div
                        className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-medium ${
                          step <= wizardStep
                            ? 'bg-stone-900 text-white'
                            : 'bg-stone-100 text-stone-400'
                        }`}
                      >
                        {step}
                      </div>
                      {step < 3 && (
                        <div
                          className={`flex-1 h-0.5 mx-2 ${
                            step < wizardStep ? 'bg-stone-900' : 'bg-stone-100'
                          }`}
                        />
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6">
              {error && (
                <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm mb-4">
                  {error}
                </div>
              )}

              {/* Step 1: Basic Info */}
              {(wizardStep === 1 || editingLink) && (
                <div className="space-y-4">
                  {!editingLink && (
                    <h3 className="font-medium text-stone-900">Basic Information</h3>
                  )}

                  <div>
                    <Label htmlFor="name">Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={e => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g., Engineering Phone Screen"
                      required
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="description">Description</Label>
                    <textarea
                      id="description"
                      value={formData.description}
                      onChange={e => setFormData({ ...formData, description: e.target.value })}
                      placeholder="Brief description shown to candidates..."
                      rows={2}
                      className="mt-1 w-full px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-stone-900/10 focus:border-stone-300"
                    />
                  </div>

                  <div>
                    <Label>Duration *</Label>
                    <div className="grid grid-cols-5 gap-2 mt-2">
                      {DURATION_OPTIONS.map(option => (
                        <button
                          key={option.value}
                          type="button"
                          onClick={() => setFormData({ ...formData, durationMinutes: option.value })}
                          className={`py-2 px-3 rounded-lg border text-sm transition-colors ${
                            formData.durationMinutes === option.value
                              ? 'border-stone-900 bg-stone-50 text-stone-900'
                              : 'border-stone-200 text-stone-600 hover:border-stone-300'
                          }`}
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {editingLink && (
                    <>
                      {/* Show all sections for edit mode */}
                      <div className="border-t border-stone-100 pt-4 mt-4">
                        <h3 className="font-medium text-stone-900 mb-4">Interviewers</h3>
                        <InterviewerSelect
                          teamMembers={activeTeamMembers}
                          selectedIds={formData.interviewerIds}
                          onChange={ids => setFormData({ ...formData, interviewerIds: ids })}
                          showLoadInfo={true}
                        />
                      </div>

                      <div className="border-t border-stone-100 pt-4 mt-4">
                        <h3 className="font-medium text-stone-900 mb-4">Booking Settings</h3>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="bufferBefore">Buffer Before (minutes)</Label>
                            <Input
                              id="bufferBefore"
                              type="number"
                              min={0}
                              max={60}
                              value={formData.bufferBeforeMinutes}
                              onChange={e => setFormData({ ...formData, bufferBeforeMinutes: parseInt(e.target.value) || 0 })}
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label htmlFor="bufferAfter">Buffer After (minutes)</Label>
                            <Input
                              id="bufferAfter"
                              type="number"
                              min={0}
                              max={60}
                              value={formData.bufferAfterMinutes}
                              onChange={e => setFormData({ ...formData, bufferAfterMinutes: parseInt(e.target.value) || 0 })}
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label htmlFor="minNotice">Min Notice (hours)</Label>
                            <Input
                              id="minNotice"
                              type="number"
                              min={1}
                              max={168}
                              value={formData.minNoticeHours}
                              onChange={e => setFormData({ ...formData, minNoticeHours: parseInt(e.target.value) || 24 })}
                              className="mt-1"
                            />
                          </div>
                          <div>
                            <Label htmlFor="maxDays">Max Days Ahead</Label>
                            <Input
                              id="maxDays"
                              type="number"
                              min={1}
                              max={90}
                              value={formData.maxDaysAhead}
                              onChange={e => setFormData({ ...formData, maxDaysAhead: parseInt(e.target.value) || 14 })}
                              className="mt-1"
                            />
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Step 2: Select Interviewers (create mode only) */}
              {wizardStep === 2 && !editingLink && (
                <div className="space-y-4">
                  <h3 className="font-medium text-stone-900">Select Interviewers</h3>
                  <p className="text-sm text-stone-500">
                    Choose who will be available to conduct interviews. Candidates will be matched with available interviewers.
                  </p>

                  {activeTeamMembers.length === 0 ? (
                    <div className="text-center py-8 bg-stone-50 rounded-lg">
                      <p className="text-stone-600 mb-2">No team members available</p>
                      <p className="text-sm text-stone-400">
                        Add team members in the Team Management page first
                      </p>
                    </div>
                  ) : (
                    <InterviewerSelect
                      teamMembers={activeTeamMembers}
                      selectedIds={formData.interviewerIds}
                      onChange={ids => setFormData({ ...formData, interviewerIds: ids })}
                      showLoadInfo={true}
                    />
                  )}
                </div>
              )}

              {/* Step 3: Booking Settings (create mode only) */}
              {wizardStep === 3 && !editingLink && (
                <div className="space-y-4">
                  <h3 className="font-medium text-stone-900">Booking Settings</h3>
                  <p className="text-sm text-stone-500">
                    Configure how far in advance candidates can book and buffer times between interviews.
                  </p>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="bufferBefore">Buffer Before (minutes)</Label>
                      <Input
                        id="bufferBefore"
                        type="number"
                        min={0}
                        max={60}
                        value={formData.bufferBeforeMinutes}
                        onChange={e => setFormData({ ...formData, bufferBeforeMinutes: parseInt(e.target.value) || 0 })}
                        className="mt-1"
                      />
                      <p className="text-xs text-stone-400 mt-1">Time before interview starts</p>
                    </div>
                    <div>
                      <Label htmlFor="bufferAfter">Buffer After (minutes)</Label>
                      <Input
                        id="bufferAfter"
                        type="number"
                        min={0}
                        max={60}
                        value={formData.bufferAfterMinutes}
                        onChange={e => setFormData({ ...formData, bufferAfterMinutes: parseInt(e.target.value) || 0 })}
                        className="mt-1"
                      />
                      <p className="text-xs text-stone-400 mt-1">Time after interview ends</p>
                    </div>
                    <div>
                      <Label htmlFor="minNotice">Minimum Notice (hours)</Label>
                      <Input
                        id="minNotice"
                        type="number"
                        min={1}
                        max={168}
                        value={formData.minNoticeHours}
                        onChange={e => setFormData({ ...formData, minNoticeHours: parseInt(e.target.value) || 24 })}
                        className="mt-1"
                      />
                      <p className="text-xs text-stone-400 mt-1">How far in advance to book</p>
                    </div>
                    <div>
                      <Label htmlFor="maxDays">Maximum Days Ahead</Label>
                      <Input
                        id="maxDays"
                        type="number"
                        min={1}
                        max={90}
                        value={formData.maxDaysAhead}
                        onChange={e => setFormData({ ...formData, maxDaysAhead: parseInt(e.target.value) || 14 })}
                        className="mt-1"
                      />
                      <p className="text-xs text-stone-400 mt-1">How far out candidates can book</p>
                    </div>
                  </div>

                  {/* Summary */}
                  <div className="mt-6 p-4 bg-stone-50 rounded-lg border border-stone-100">
                    <h4 className="font-medium text-stone-900 mb-2">Summary</h4>
                    <ul className="text-sm text-stone-600 space-y-1">
                      <li><span className="text-stone-400">Name:</span> {formData.name}</li>
                      <li><span className="text-stone-400">Duration:</span> {formData.durationMinutes} minutes</li>
                      <li><span className="text-stone-400">Interviewers:</span> {formData.interviewerIds.length} selected</li>
                      <li><span className="text-stone-400">Booking window:</span> {formData.minNoticeHours}h notice, up to {formData.maxDaysAhead} days ahead</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t flex justify-between">
              <div>
                {!editingLink && wizardStep > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setWizardStep(wizardStep - 1)}
                  >
                    Back
                  </Button>
                )}
              </div>

              <div className="flex gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCreateModal(false)
                    setEditingLink(null)
                    resetForm()
                  }}
                >
                  Cancel
                </Button>

                {editingLink ? (
                  <Button onClick={handleUpdateLink} disabled={isSaving || !formData.name}>
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </Button>
                ) : wizardStep < 3 ? (
                  <Button
                    onClick={() => setWizardStep(wizardStep + 1)}
                    disabled={
                      (wizardStep === 1 && !formData.name) ||
                      (wizardStep === 2 && formData.interviewerIds.length === 0)
                    }
                  >
                    Next
                  </Button>
                ) : (
                  <Button onClick={handleCreateLink} disabled={isSaving}>
                    {isSaving ? 'Creating...' : 'Create Link'}
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </PageWrapper>
  )
}
