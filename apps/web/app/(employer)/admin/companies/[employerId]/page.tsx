'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AdminNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface EmployerDetailJob {
  id: string
  title: string
  vertical: string | null
  role_type: string | null
  location: string | null
  salary_min: number | null
  salary_max: number | null
  requirements: string[] | null
  description: string | null
  is_active: boolean
  created_at: string
}

interface EmployerDetailMatch {
  candidate_id: string
  candidate_name: string
  candidate_email: string
  university: string | null
  match_score: number
  status: string
  job_title: string | null
}

interface EmployerDetailFounder {
  name: string
  title: string | null
  linkedin: string | null
}

interface EmployerDetail {
  id: string
  company_name: string
  email: string
  industry: string | null
  company_size: string | null
  website: string | null
  is_verified: boolean
  created_at: string
  organization_description: string | null
  founders: EmployerDetailFounder[]
  jobs: EmployerDetailJob[]
  matches: EmployerDetailMatch[]
}

function formatSalary(min: number | null, max: number | null): string {
  if (!min && !max) return '-'
  const fmt = (n: number) => `$${(n / 1000).toFixed(0)}k`
  if (min && max) return `${fmt(min)} - ${fmt(max)}`
  if (min) return `${fmt(min)}+`
  return `Up to ${fmt(max!)}`
}

function formatVertical(v: string | null): string {
  if (!v) return '-'
  return v.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const statusColors: Record<string, string> = {
  PENDING: 'bg-stone-100 text-stone-600',
  CONTACTED: 'bg-teal-50 text-teal-700',
  IN_REVIEW: 'bg-amber-50 text-amber-700',
  SHORTLISTED: 'bg-teal-50 text-teal-700',
  REJECTED: 'bg-red-50 text-red-700',
  HIRED: 'bg-teal-50 text-teal-700',
  WATCHLIST: 'bg-stone-100 text-stone-600',
}

export default function CompanyDetailPage() {
  const params = useParams()
  const router = useRouter()
  const employerId = params.employerId as string

  const [data, setData] = useState<EmployerDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const password = localStorage.getItem('admin_password')
    if (!password) {
      router.push('/admin')
      return
    }

    fetch(`${API_BASE_URL}/api/admin/employers/${employerId}/detail`, {
      headers: { 'X-Admin-Password': password },
    })
      .then(async res => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Failed to load' }))
          throw new Error(err.detail || 'Failed to load')
        }
        return res.json()
      })
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [employerId, router])

  if (loading) {
    return (
      <>
        <AdminNavbar />
        <PageWrapper>
          <Container>
            <div className="flex items-center justify-center py-24">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-stone-300 border-t-stone-600" />
            </div>
          </Container>
        </PageWrapper>
      </>
    )
  }

  if (error || !data) {
    return (
      <>
        <AdminNavbar />
        <PageWrapper>
          <Container>
            <div className="py-12 text-center">
              <p className="text-stone-500 mb-4">{error || 'Company not found'}</p>
              <Button variant="outline" onClick={() => router.push('/admin')} className="border-stone-200 text-stone-600 hover:bg-stone-50 rounded-lg">
                Back to Admin
              </Button>
            </div>
          </Container>
        </PageWrapper>
      </>
    )
  }

  return (
    <>
      <AdminNavbar />
      <PageWrapper>
        <Container>
          <div className="space-y-6">
            {/* Back button */}
            <button
              onClick={() => router.push('/admin')}
              className="flex items-center gap-1.5 text-sm text-stone-500 hover:text-stone-700 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Admin
            </button>

            {/* Company Header */}
            <Card className="border border-stone-200 rounded-2xl shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <h1 className="text-2xl font-semibold text-stone-900">{data.company_name}</h1>
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                        data.is_verified ? 'bg-teal-50 text-teal-700' : 'bg-amber-50 text-amber-700'
                      }`}>
                        {data.is_verified ? 'Verified' : 'Unverified'}
                      </span>
                    </div>
                    <p className="text-sm text-stone-500 mt-1">{data.email}</p>
                    {data.organization_description && (
                      <p className="text-sm text-stone-600 mt-3 max-w-2xl">{data.organization_description}</p>
                    )}
                  </div>
                </div>

                <div className="flex flex-wrap gap-4 mt-4 text-sm text-stone-500">
                  {data.industry && (
                    <span className="flex items-center gap-1.5">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
                      {data.industry}
                    </span>
                  )}
                  {data.company_size && (
                    <span className="flex items-center gap-1.5">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                      {data.company_size}
                    </span>
                  )}
                  {data.website && (
                    <a href={data.website.startsWith('http') ? data.website : `https://${data.website}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 text-teal-700 hover:underline">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
                      Website
                    </a>
                  )}
                  <span className="flex items-center gap-1.5">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                    Joined {new Date(data.created_at).toLocaleDateString()}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Founders */}
            {data.founders.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-stone-900 mb-3">Founders</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {data.founders.map((f, i) => (
                    <Card key={i} className="border border-stone-200 rounded-xl shadow-sm">
                      <CardContent className="p-4">
                        <p className="text-sm font-medium text-stone-800">{f.name}</p>
                        {f.title && <p className="text-xs text-stone-500 mt-0.5">{f.title}</p>}
                        {f.linkedin && (
                          <a href={f.linkedin.startsWith('http') ? f.linkedin : `https://${f.linkedin}`} target="_blank" rel="noopener noreferrer" className="text-xs text-teal-700 hover:underline mt-1 inline-block">
                            LinkedIn
                          </a>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Jobs */}
            <div>
              <h2 className="text-lg font-semibold text-stone-900 mb-3">
                Jobs <span className="text-sm font-normal text-stone-400">({data.jobs.length})</span>
              </h2>
              {data.jobs.length === 0 ? (
                <Card className="border border-stone-200 rounded-xl shadow-sm">
                  <CardContent className="p-6 text-center">
                    <p className="text-sm text-stone-400">No jobs posted yet</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="overflow-x-auto rounded-xl border border-stone-200 shadow-sm">
                  <table className="min-w-full divide-y divide-stone-100">
                    <thead className="bg-stone-50/50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Title</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Vertical</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Location</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Salary</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Status</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Created</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-100">
                      {data.jobs.map(j => (
                        <tr key={j.id} className="hover:bg-stone-50/50 transition-colors">
                          <td className="px-4 py-3 text-sm font-medium text-stone-800">{j.title}</td>
                          <td className="px-4 py-3 text-sm text-stone-500">{formatVertical(j.vertical)}</td>
                          <td className="px-4 py-3 text-sm text-stone-500">{j.location || '-'}</td>
                          <td className="px-4 py-3 text-sm text-stone-500">{formatSalary(j.salary_min, j.salary_max)}</td>
                          <td className="px-4 py-3">
                            <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                              j.is_active ? 'bg-teal-50 text-teal-700' : 'bg-stone-100 text-stone-500'
                            }`}>
                              {j.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-stone-400">{new Date(j.created_at).toLocaleDateString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Matched Students */}
            <div>
              <h2 className="text-lg font-semibold text-stone-900 mb-3">
                Matched Students <span className="text-sm font-normal text-stone-400">({data.matches.length})</span>
              </h2>
              {data.matches.length === 0 ? (
                <Card className="border border-stone-200 rounded-xl shadow-sm">
                  <CardContent className="p-6 text-center">
                    <p className="text-sm text-stone-400">No matched students yet</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="overflow-x-auto rounded-xl border border-stone-200 shadow-sm">
                  <table className="min-w-full divide-y divide-stone-100">
                    <thead className="bg-stone-50/50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Name</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Email</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">University</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Job</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Score</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-stone-500 uppercase tracking-wider">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-100">
                      {data.matches.map((m, i) => (
                        <tr key={i} className="hover:bg-stone-50/50 transition-colors">
                          <td className="px-4 py-3 text-sm font-medium text-stone-800">{m.candidate_name}</td>
                          <td className="px-4 py-3 text-sm text-stone-500">{m.candidate_email}</td>
                          <td className="px-4 py-3 text-sm text-stone-500">{m.university || '-'}</td>
                          <td className="px-4 py-3 text-sm text-stone-500">{m.job_title || '-'}</td>
                          <td className="px-4 py-3 text-sm text-stone-600 font-medium">{m.match_score.toFixed(1)}</td>
                          <td className="px-4 py-3">
                            <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${statusColors[m.status] || 'bg-stone-100 text-stone-600'}`}>
                              {m.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </Container>
      </PageWrapper>
    </>
  )
}
