'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { employerApi, type Employer } from '@/lib/api'

const INDUSTRY_OPTIONS = [
  { value: '', label: 'Select industry' },
  { value: 'tech', label: 'Technology' },
  { value: 'finance', label: 'Finance' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'retail', label: 'Retail' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'education', label: 'Education' },
  { value: 'consulting', label: 'Consulting' },
  { value: 'other', label: 'Other' },
]

const COMPANY_SIZE_OPTIONS = [
  { value: '', label: 'Select size' },
  { value: '1-10', label: '1-10 employees' },
  { value: '11-50', label: '11-50 employees' },
  { value: '51-200', label: '51-200 employees' },
  { value: '201-500', label: '201-500 employees' },
  { value: '501-1000', label: '501-1000 employees' },
  { value: '1000+', label: '1000+ employees' },
]

export default function EmployerSettingsPage() {
  const router = useRouter()
  const [employer, setEmployer] = useState<Employer | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Form state
  const [name, setName] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [industry, setIndustry] = useState('')
  const [companySize, setCompanySize] = useState('')

  // Dropdown state
  const [industryOpen, setIndustryOpen] = useState(false)
  const [companySizeOpen, setCompanySizeOpen] = useState(false)
  const industryRef = useRef<HTMLDivElement>(null)
  const companySizeRef = useRef<HTMLDivElement>(null)

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (industryRef.current && !industryRef.current.contains(event.target as Node)) {
        setIndustryOpen(false)
      }
      if (companySizeRef.current && !companySizeRef.current.contains(event.target as Node)) {
        setCompanySizeOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const token = localStorage.getItem('employer_token')
        if (!token) {
          router.push('/login')
          return
        }

        const data = await employerApi.getMe()
        setEmployer(data)
        setName(data.name || '')
        setCompanyName(data.companyName || '')
        setIndustry(data.industry || '')
        setCompanySize(data.companySize || '')
      } catch (err) {
        console.error('Failed to load profile:', err)
        if (err instanceof Error && err.message.includes('401')) {
          localStorage.removeItem('employer_token')
          router.push('/login')
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadProfile()
  }, [router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setIsSaving(true)

    try {
      const updated = await employerApi.updateProfile({
        name: name || undefined,
        companyName: companyName || undefined,
        industry: industry || undefined,
        companySize: companySize || undefined,
      })

      setEmployer(updated)
      // Update localStorage
      localStorage.setItem('employer', JSON.stringify(updated))
      setSuccess('Profile updated successfully!')

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-stone-200 border-t-teal-600 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-stone-400 text-sm">Loading...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-100 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-stone-400 hover:text-stone-600 transition-colors">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Link>
            <h1 className="text-lg font-semibold text-stone-900">Account Settings</h1>
          </div>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-6 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Profile Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Profile Information</CardTitle>
              <CardDescription>Update your personal and company details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="grid sm:grid-cols-2 gap-5">
                <div>
                  <Label htmlFor="name" className="text-sm font-medium text-stone-700">
                    Your Name
                  </Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="John Smith"
                    className="mt-2"
                  />
                  <p className="text-xs text-stone-500 mt-1">This will be displayed in your profile avatar</p>
                </div>
                <div>
                  <Label htmlFor="companyName" className="text-sm font-medium text-stone-700">
                    Company Name
                  </Label>
                  <Input
                    id="companyName"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="Acme Corp"
                    className="mt-2"
                    required
                  />
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-5">
                {/* Custom Industry Dropdown */}
                <div>
                  <Label htmlFor="industry" className="text-sm font-medium text-stone-700">
                    Industry
                  </Label>
                  <div ref={industryRef} className="relative mt-2">
                    <button
                      type="button"
                      onClick={() => { setIndustryOpen(!industryOpen); setCompanySizeOpen(false) }}
                      className="w-full h-10 px-3 flex items-center justify-between rounded-lg border border-stone-200 text-sm bg-white hover:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-900/10 transition-colors"
                    >
                      <span className={industry ? 'text-stone-900' : 'text-stone-400'}>
                        {INDUSTRY_OPTIONS.find(o => o.value === industry)?.label || 'Select industry'}
                      </span>
                      <svg className={`w-4 h-4 text-stone-400 transition-transform ${industryOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {industryOpen && (
                      <div className="absolute z-20 mt-1 w-full max-w-[calc(100vw-2rem)] bg-white border border-stone-200 rounded-lg shadow-lg py-1 max-h-60 overflow-auto">
                        {INDUSTRY_OPTIONS.map(option => (
                          <button
                            key={option.value}
                            type="button"
                            onClick={() => { setIndustry(option.value); setIndustryOpen(false) }}
                            className={`w-full px-3 py-2 text-left text-sm transition-colors
                              ${industry === option.value
                                ? 'bg-stone-50 text-stone-900 font-medium'
                                : 'text-stone-700 hover:bg-stone-50'
                              }`}
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Custom Company Size Dropdown */}
                <div>
                  <Label htmlFor="companySize" className="text-sm font-medium text-stone-700">
                    Company Size
                  </Label>
                  <div ref={companySizeRef} className="relative mt-2">
                    <button
                      type="button"
                      onClick={() => { setCompanySizeOpen(!companySizeOpen); setIndustryOpen(false) }}
                      className="w-full h-10 px-3 flex items-center justify-between rounded-lg border border-stone-200 text-sm bg-white hover:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-900/10 transition-colors"
                    >
                      <span className={companySize ? 'text-stone-900' : 'text-stone-400'}>
                        {COMPANY_SIZE_OPTIONS.find(o => o.value === companySize)?.label || 'Select size'}
                      </span>
                      <svg className={`w-4 h-4 text-stone-400 transition-transform ${companySizeOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {companySizeOpen && (
                      <div className="absolute z-20 mt-1 w-full max-w-[calc(100vw-2rem)] bg-white border border-stone-200 rounded-lg shadow-lg py-1 max-h-60 overflow-auto">
                        {COMPANY_SIZE_OPTIONS.map(option => (
                          <button
                            key={option.value}
                            type="button"
                            onClick={() => { setCompanySize(option.value); setCompanySizeOpen(false) }}
                            className={`w-full px-3 py-2 text-left text-sm transition-colors
                              ${companySize === option.value
                                ? 'bg-stone-50 text-stone-900 font-medium'
                                : 'text-stone-700 hover:bg-stone-50'
                              }`}
                          >
                            {option.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Account Information (Read-only) */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Account Information</CardTitle>
              <CardDescription>Your account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-sm font-medium text-stone-700">Email</Label>
                <p className="mt-1 text-stone-600">{employer?.email}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-stone-700">Account Status</Label>
                <p className="mt-1">
                  {employer?.isVerified ? (
                    <span className="inline-flex items-center gap-1 text-green-600">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      Verified
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-amber-600">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      Pending verification
                    </span>
                  )}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-stone-700">Member Since</Label>
                <p className="mt-1 text-stone-600">
                  {employer?.createdAt ? new Date(employer.createdAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  }) : '-'}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Error/Success Messages */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {success && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
              <p className="text-sm text-green-600">{success}</p>
            </div>
          )}

          {/* Save Button */}
          <div className="flex justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push('/dashboard')}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSaving}
              className="bg-teal-600 hover:bg-teal-700"
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </div>
    </main>
  )
}
