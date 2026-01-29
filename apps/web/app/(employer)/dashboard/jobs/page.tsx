'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { employerApi, inviteApi, type Job, type InviteTokenResponse } from '@/lib/api'

type ViewMode = 'list' | 'create' | 'detail'

// Vertical and Role Type definitions
const VERTICALS = [
  { value: 'new_energy', label: 'New Energy / EV', description: 'Battery, embedded, autonomous driving' },
  { value: 'sales', label: 'Sales / BD', description: 'Sales reps, BD managers, account managers' },
]

const ROLE_TYPES: Record<string, { value: string; label: string }[]> = {
  new_energy: [
    { value: 'battery_engineer', label: 'Battery Engineer' },
    { value: 'embedded_software', label: 'Embedded Software Engineer' },
    { value: 'autonomous_driving', label: 'Autonomous Driving Engineer' },
    { value: 'supply_chain', label: 'Supply Chain Manager' },
    { value: 'ev_sales', label: 'EV Sales' },
  ],
  sales: [
    { value: 'sales_rep', label: 'Sales Representative' },
    { value: 'bd_manager', label: 'BD Manager' },
    { value: 'account_manager', label: 'Account Manager' },
  ],
}

export default function JobsPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [invites, setInvites] = useState<InviteTokenResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    requirements: '',
    location: '',
    salaryMin: '',
    salaryMax: '',
    vertical: '',
    roleType: '',
  })

  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      setIsLoading(true)
      const data = await employerApi.listJobs()
      setJobs(data.jobs)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs')
    } finally {
      setIsLoading(false)
    }
  }

  const loadInvites = async (jobId: string) => {
    try {
      const data = await inviteApi.listTokens(jobId)
      setInvites(data.tokens)
    } catch (err) {
      console.error('Failed to load invites', err)
    }
  }

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setError(null)

    try {
      const requirements = formData.requirements
        .split('\n')
        .map(r => r.trim())
        .filter(r => r.length > 0)

      await employerApi.createJob({
        title: formData.title,
        description: formData.description,
        requirements,
        location: formData.location || undefined,
        salaryMin: formData.salaryMin ? parseInt(formData.salaryMin) : undefined,
        salaryMax: formData.salaryMax ? parseInt(formData.salaryMax) : undefined,
        vertical: formData.vertical || undefined,
        roleType: formData.roleType || undefined,
      })

      setFormData({
        title: '',
        description: '',
        requirements: '',
        location: '',
        salaryMin: '',
        salaryMax: '',
        vertical: '',
        roleType: '',
      })
      setViewMode('list')
      loadJobs()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create job')
    } finally {
      setIsSaving(false)
    }
  }

  const handleSelectJob = async (job: Job) => {
    setSelectedJob(job)
    await loadInvites(job.id)
    setViewMode('detail')
  }

  const handleCreateInvite = async () => {
    if (!selectedJob) return

    try {
      await inviteApi.createToken(selectedJob.id, 0, 30)
      await loadInvites(selectedJob.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create invite')
    }
  }

  const handleCopyLink = async (url: string, id: string) => {
    try {
      await navigator.clipboard.writeText(url)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch {
      // Fallback
    }
  }

  const handleDeleteInvite = async (inviteId: string) => {
    try {
      await inviteApi.deleteToken(inviteId)
      if (selectedJob) {
        await loadInvites(selectedJob.id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete invite')
    }
  }

  const handleVerticalChange = (vertical: string) => {
    setFormData({ ...formData, vertical, roleType: '' })
  }

  const getVerticalLabel = (value: string) => {
    return VERTICALS.find(v => v.value === value)?.label || value
  }

  const getRoleTypeLabel = (vertical: string, roleType: string) => {
    return ROLE_TYPES[vertical]?.find(r => r.value === roleType)?.label || roleType
  }

  if (isLoading) {
    return (
      <div className="p-6 sm:p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded-xl"></div>
          <div className="h-32 bg-gray-200 rounded-xl"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {viewMode === 'list' && 'Jobs'}
            {viewMode === 'create' && 'Create New Job'}
            {viewMode === 'detail' && selectedJob?.title}
          </h1>
          <p className="text-gray-500 mt-1">
            {viewMode === 'list' && `${jobs.length} job${jobs.length !== 1 ? 's' : ''} posted`}
            {viewMode === 'create' && 'Add a new position to start interviewing candidates'}
            {viewMode === 'detail' && 'Manage job details and invite links'}
          </p>
        </div>
        <div className="flex gap-3">
          {viewMode !== 'list' && (
            <Button
              variant="outline"
              onClick={() => {
                setViewMode('list')
                setSelectedJob(null)
              }}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Jobs
            </Button>
          )}
          {viewMode === 'list' && (
            <Button onClick={() => setViewMode('create')}>
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Job
            </Button>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
          <button onClick={() => setError(null)} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      {/* Job List */}
      {viewMode === 'list' && (
        <div className="space-y-4">
          {jobs.length === 0 ? (
            <div className="text-center py-16 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs yet</h3>
              <p className="text-gray-500 mb-4">Create your first job posting to start interviewing candidates</p>
              <Button onClick={() => setViewMode('create')}>Create Job</Button>
            </div>
          ) : (
            jobs.map((job) => (
              <div
                key={job.id}
                onClick={() => handleSelectJob(job)}
                className="bg-white border border-gray-200 rounded-xl p-5 hover:border-gray-300 hover:shadow-md transition-all cursor-pointer"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2 flex-wrap">
                      <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                        job.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {job.isActive ? 'Active' : 'Inactive'}
                      </span>
                      {job.vertical && (
                        <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-100 text-emerald-700">
                          {getVerticalLabel(job.vertical)}
                        </span>
                      )}
                      {job.roleType && (
                        <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-700">
                          {getRoleTypeLabel(job.vertical || '', job.roleType)}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 text-sm line-clamp-2 mb-3">{job.description}</p>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                      {job.location && (
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          {job.location}
                        </span>
                      )}
                      {(job.salaryMin || job.salaryMax) && (
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          ¥{job.salaryMin?.toLocaleString() || '?'} - ¥{job.salaryMax?.toLocaleString() || '?'}
                        </span>
                      )}
                    </div>
                  </div>
                  <svg className="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Create Job Form */}
      {viewMode === 'create' && (
        <form onSubmit={handleCreateJob} className="bg-white border border-gray-200 rounded-xl p-6">
          <div className="space-y-6">
            {/* Vertical Selection */}
            <div>
              <Label className="text-sm font-medium">Industry Vertical *</Label>
              <p className="text-xs text-gray-500 mb-3">This determines the interview questions template</p>
              <div className="grid sm:grid-cols-2 gap-3">
                {VERTICALS.map((v) => (
                  <button
                    key={v.value}
                    type="button"
                    onClick={() => handleVerticalChange(v.value)}
                    className={`p-4 rounded-xl border-2 text-left transition-all ${
                      formData.vertical === v.value
                        ? 'border-emerald-500 bg-emerald-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{v.label}</div>
                    <div className="text-sm text-gray-500">{v.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Role Type Selection */}
            {formData.vertical && ROLE_TYPES[formData.vertical] && (
              <div>
                <Label className="text-sm font-medium">Role Type *</Label>
                <p className="text-xs text-gray-500 mb-3">Select the specific role for tailored interview questions</p>
                <div className="grid sm:grid-cols-3 gap-3">
                  {ROLE_TYPES[formData.vertical].map((r) => (
                    <button
                      key={r.value}
                      type="button"
                      onClick={() => setFormData({ ...formData, roleType: r.value })}
                      className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                        formData.roleType === r.value
                          ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                          : 'border-gray-200 text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      {r.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div>
              <Label htmlFor="title" className="text-sm font-medium">Job Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g. Senior Battery Engineer"
                className="mt-2"
                required
              />
            </div>

            <div>
              <Label htmlFor="description" className="text-sm font-medium">Description *</Label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe the role, responsibilities, and what you're looking for..."
                className="mt-2 w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[120px] resize-y"
                required
              />
            </div>

            <div>
              <Label htmlFor="requirements" className="text-sm font-medium">Requirements (one per line)</Label>
              <textarea
                id="requirements"
                value={formData.requirements}
                onChange={(e) => setFormData({ ...formData, requirements: e.target.value })}
                placeholder="5+ years of battery engineering experience&#10;Experience with lithium-ion cell design&#10;Strong problem-solving skills"
                className="mt-2 w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-[100px] resize-y font-mono text-sm"
              />
            </div>

            <div className="grid sm:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="location" className="text-sm font-medium">Location</Label>
                <Input
                  id="location"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="e.g. Shanghai"
                  className="mt-2"
                />
              </div>
              <div>
                <Label htmlFor="salaryMin" className="text-sm font-medium">Min Salary (¥/month)</Label>
                <Input
                  id="salaryMin"
                  type="number"
                  value={formData.salaryMin}
                  onChange={(e) => setFormData({ ...formData, salaryMin: e.target.value })}
                  placeholder="15000"
                  className="mt-2"
                />
              </div>
              <div>
                <Label htmlFor="salaryMax" className="text-sm font-medium">Max Salary (¥/month)</Label>
                <Input
                  id="salaryMax"
                  type="number"
                  value={formData.salaryMax}
                  onChange={(e) => setFormData({ ...formData, salaryMax: e.target.value })}
                  placeholder="30000"
                  className="mt-2"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={() => setViewMode('list')}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSaving || !formData.vertical || !formData.roleType}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                {isSaving ? 'Creating...' : 'Create Job'}
              </Button>
            </div>
          </div>
        </form>
      )}

      {/* Job Detail View */}
      {viewMode === 'detail' && selectedJob && (
        <div className="space-y-6">
          {/* Job Info Card */}
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{selectedJob.title}</h2>
                <div className="flex flex-wrap items-center gap-2 mt-2">
                  {selectedJob.vertical && (
                    <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-100 text-emerald-700">
                      {getVerticalLabel(selectedJob.vertical)}
                    </span>
                  )}
                  {selectedJob.roleType && (
                    <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-700">
                      {getRoleTypeLabel(selectedJob.vertical || '', selectedJob.roleType)}
                    </span>
                  )}
                  {selectedJob.location && (
                    <span className="text-sm text-gray-500">{selectedJob.location}</span>
                  )}
                  {(selectedJob.salaryMin || selectedJob.salaryMax) && (
                    <span className="text-sm text-gray-500">
                      ¥{selectedJob.salaryMin?.toLocaleString()} - ¥{selectedJob.salaryMax?.toLocaleString()}
                    </span>
                  )}
                </div>
              </div>
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                selectedJob.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
              }`}>
                {selectedJob.isActive ? 'Active' : 'Inactive'}
              </span>
            </div>
            <p className="text-gray-600 mb-4">{selectedJob.description}</p>
            {selectedJob.requirements && selectedJob.requirements.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Requirements</h4>
                <ul className="space-y-1">
                  {selectedJob.requirements.map((req, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                      <svg className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {req}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Invite Links Card */}
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Interview Invite Links</h3>
                <p className="text-sm text-gray-500">Share these links with candidates to start interviews</p>
              </div>
              <Button onClick={handleCreateInvite} className="bg-emerald-600 hover:bg-emerald-700">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Link
              </Button>
            </div>

            {invites.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <svg className="w-10 h-10 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                <p className="text-gray-500">No invite links yet. Create one to start collecting interviews.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {invites.map((invite) => (
                  <div key={invite.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-mono text-gray-700 truncate">{invite.inviteUrl}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        Used: {invite.usedCount}/{invite.maxUses || '∞'}
                        {invite.expiresAt && ` · Expires: ${new Date(invite.expiresAt).toLocaleDateString()}`}
                        {!invite.isActive && ' · Inactive'}
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopyLink(invite.inviteUrl, invite.id)}
                      className="flex-shrink-0"
                    >
                      {copiedId === invite.id ? (
                        <>
                          <svg className="w-4 h-4 mr-1 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Copied
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          Copy
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteInvite(invite.id)}
                      className="flex-shrink-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="flex gap-3">
            <Link href={`/dashboard/interviews?job_id=${selectedJob.id}`}>
              <Button variant="outline">
                View Interviews for This Job
              </Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
