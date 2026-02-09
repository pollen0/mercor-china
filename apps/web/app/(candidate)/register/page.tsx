'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { candidateRegistrationSchema, targetRoleOptions, majorOptions, universityOptions, graduationYearOptions, type CandidateRegistrationInput } from '@/lib/validations/candidate'
import { setAuthTokens } from '@/lib/auth'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type FormErrors = Partial<Record<keyof CandidateRegistrationInput, string>>

// GitHub signup removed - we need school/graduation info that GitHub can't provide
// GitHub can be connected after registration on the dashboard

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState<CandidateRegistrationInput>({
    name: '',
    email: '',
    phone: '',
    password: '',
    university: '',
    graduationYear: undefined,
    major: '',
    targetRoles: [],
  })
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState<FormErrors & { confirmPassword?: string }>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const [selectedMajors, setSelectedMajors] = useState<string[]>([])
  const [customMajor, setCustomMajor] = useState('')
  const [majorDropdownOpen, setMajorDropdownOpen] = useState(false)
  const majorDropdownRef = useRef<HTMLDivElement>(null)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }))
    }
  }

  const handleRoleToggle = (role: string) => {
    setFormData(prev => ({
      ...prev,
      targetRoles: prev.targetRoles.includes(role)
        ? prev.targetRoles.filter(r => r !== role)
        : [...prev.targetRoles, role],
    }))
  }

  const handleMajorToggle = (major: string) => {
    const updated = selectedMajors.includes(major)
      ? selectedMajors.filter(m => m !== major)
      : [...selectedMajors, major]
    setSelectedMajors(updated)
    // If removing "Other", clear custom input
    if (major === 'Other' && selectedMajors.includes('Other')) {
      setCustomMajor('')
    }
    // Join into comma-separated string for backend
    const allMajors = updated
      .map(m => m === 'Other' && customMajor ? customMajor : m)
      .filter(m => m !== 'Other')
    if (updated.includes('Other') && customMajor) {
      allMajors.push(customMajor)
    }
    setFormData(prev => ({ ...prev, major: allMajors.join(', ') }))
  }

  const handleCustomMajorChange = (value: string) => {
    setCustomMajor(value)
    // Update the joined major string
    const allMajors = selectedMajors
      .filter(m => m !== 'Other')
    if (value) allMajors.push(value)
    setFormData(prev => ({ ...prev, major: allMajors.join(', ') }))
  }

  // Close major dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (majorDropdownRef.current && !majorDropdownRef.current.contains(e.target as Node)) {
        setMajorDropdownOpen(false)
      }
    }
    if (majorDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [majorDropdownOpen])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})
    setSubmitStatus('idle')
    setErrorMessage('')

    // Check passwords match
    if (formData.password !== confirmPassword) {
      setErrors({ confirmPassword: 'Passwords do not match' })
      return
    }

    const result = candidateRegistrationSchema.safeParse(formData)

    if (!result.success) {
      const fieldErrors: FormErrors = {}
      result.error.errors.forEach(err => {
        if (err.path[0]) {
          fieldErrors[err.path[0] as keyof FormErrors] = err.message
        }
      })
      setErrors(fieldErrors)
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/candidates/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result.data),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Registration failed. Please try again.')
      }

      // Store candidate info
      localStorage.setItem('candidate', JSON.stringify({
        id: data.candidate.id,
        name: data.candidate.name,
        email: data.candidate.email,
      }))

      // Store tokens (in both localStorage and cookies for middleware)
      setAuthTokens('candidate', {
        token: data.token,
        refreshToken: data.refresh_token,
        expiresIn: data.expires_in || 3600,
      })

      setSubmitStatus('success')

      // Redirect to resume upload after short delay
      setTimeout(() => {
        router.push('/candidate/resume?onboarding=true')
      }, 1500)
    } catch (error) {
      setSubmitStatus('error')
      setErrorMessage(error instanceof Error ? error.message : 'Registration failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (submitStatus === 'success') {
    return (
      <main className="min-h-screen bg-white flex items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          <div className="w-12 h-12 bg-teal-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-6 h-6 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-xl font-semibold text-stone-900 mb-2">You're in</h1>
          <p className="text-stone-400 text-sm mb-8">
            Next: upload your resume for personalized questions.
          </p>
          <Link href="/">
            <Button variant="ghost" className="text-stone-500">Back to Home</Button>
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-white flex items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block text-xl font-semibold text-stone-900 mb-6 hover:text-stone-600 transition-colors">
            Pathway
          </Link>
          <h1 className="text-2xl font-semibold text-stone-900 mb-2">Create account</h1>
          <p className="text-stone-400 text-sm">
            Start your journey
          </p>
        </div>
        <div>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="name" className="text-stone-600 text-sm">
                Full Name
              </Label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Your name"
                className={`border-stone-200 focus:border-stone-400 focus:ring-0 ${errors.name ? 'border-red-300' : ''}`}
              />
              {errors.name && (
                <p className="text-xs text-red-500">{errors.name}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="email" className="text-stone-600 text-sm">
                Email
              </Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="you@university.edu"
                className={`border-stone-200 focus:border-stone-400 focus:ring-0 ${errors.email ? 'border-red-300' : ''}`}
              />
              {errors.email && (
                <p className="text-xs text-red-500">{errors.email}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="phone" className="text-stone-600 text-sm">
                Phone
              </Label>
              <Input
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="(555) 123-4567"
                className={`border-stone-200 focus:border-stone-400 focus:ring-0 ${errors.phone ? 'border-red-300' : ''}`}
              />
              {errors.phone && (
                <p className="text-xs text-red-500">{errors.phone}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password" className="text-stone-600 text-sm">
                Password
              </Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="At least 8 characters"
                className={`border-stone-200 focus:border-stone-400 focus:ring-0 ${errors.password ? 'border-red-300' : ''}`}
              />
              {errors.password && (
                <p className="text-xs text-red-500">{errors.password}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="confirmPassword" className="text-stone-600 text-sm">
                Confirm Password
              </Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value)
                  if (errors.confirmPassword) {
                    setErrors(prev => ({ ...prev, confirmPassword: undefined }))
                  }
                }}
                placeholder="Confirm your password"
                className={`border-stone-200 focus:border-stone-400 focus:ring-0 ${errors.confirmPassword ? 'border-red-300' : ''}`}
              />
              {errors.confirmPassword && (
                <p className="text-xs text-red-500">{errors.confirmPassword}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="university" className="text-stone-600 text-sm">
                University
              </Label>
              <select
                id="university"
                value={formData.university}
                onChange={(e) => {
                  setFormData(prev => ({ ...prev, university: e.target.value }))
                  if (errors.university) {
                    setErrors(prev => ({ ...prev, university: undefined }))
                  }
                }}
                className={`w-full h-11 px-3 rounded-lg border bg-white text-sm focus:outline-none focus:border-stone-400 ${
                  errors.university ? 'border-red-300' : 'border-stone-200'
                }`}
              >
                <option value="">Select university</option>
                {universityOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {errors.university && (
                <p className="text-xs text-red-500">{errors.university}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="graduationYear" className="text-stone-600 text-sm">Grad Year</Label>
              <select
                id="graduationYear"
                value={formData.graduationYear?.toString() || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, graduationYear: e.target.value ? parseInt(e.target.value) : undefined }))}
                className="w-full h-11 px-3 rounded-lg border border-stone-200 bg-white text-sm focus:outline-none focus:border-stone-400"
              >
                <option value="">Year</option>
                {graduationYearOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5" ref={majorDropdownRef}>
              <Label className="text-stone-600 text-sm">Major(s)</Label>
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setMajorDropdownOpen(!majorDropdownOpen)}
                  className={`w-full min-h-[2.75rem] px-3 py-2 rounded-lg border bg-white text-sm text-left flex items-center gap-1.5 flex-wrap focus:outline-none focus:border-stone-400 transition-colors ${
                    majorDropdownOpen ? 'border-stone-400' : 'border-stone-200'
                  }`}
                >
                  {selectedMajors.length === 0 ? (
                    <span className="text-stone-400">Select major(s)</span>
                  ) : (
                    selectedMajors.map(m => (
                      <span
                        key={m}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-stone-100 text-stone-700 text-xs"
                      >
                        {m === 'Other' && customMajor ? customMajor : m}
                        <span
                          role="button"
                          onClick={(e) => { e.stopPropagation(); handleMajorToggle(m) }}
                          className="text-stone-400 hover:text-stone-600 cursor-pointer"
                        >
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </span>
                      </span>
                    ))
                  )}
                  <svg className={`w-4 h-4 text-stone-400 ml-auto flex-shrink-0 transition-transform ${majorDropdownOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {majorDropdownOpen && (
                  <div className="absolute z-10 mt-1 w-full bg-white border border-stone-200 rounded-lg shadow-lg py-1 max-h-56 overflow-auto">
                    {majorOptions.map(option => (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => handleMajorToggle(option.value)}
                        className={`w-full px-3 py-2 text-left text-sm flex items-center gap-2.5 transition-colors ${
                          selectedMajors.includes(option.value)
                            ? 'bg-stone-50 text-stone-900'
                            : 'text-stone-700 hover:bg-stone-50'
                        }`}
                      >
                        <span className={`w-4 h-4 rounded border flex-shrink-0 flex items-center justify-center ${
                          selectedMajors.includes(option.value)
                            ? 'bg-stone-900 border-stone-900'
                            : 'border-stone-300'
                        }`}>
                          {selectedMajors.includes(option.value) && (
                            <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </span>
                        {option.label}
                      </button>
                    ))}
                    {selectedMajors.includes('Other') && (
                      <div className="px-3 py-2 border-t border-stone-100">
                        <input
                          type="text"
                          value={customMajor}
                          onChange={(e) => handleCustomMajorChange(e.target.value)}
                          placeholder="Type your major..."
                          className="w-full text-sm border border-stone-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
                          onClick={(e) => e.stopPropagation()}
                        />
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-stone-600 text-sm">Target Roles</Label>
              <div className="flex flex-wrap gap-2">
                {targetRoleOptions.map(option => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleRoleToggle(option.value)}
                    className={`px-3 py-1.5 text-sm rounded-full border transition-all duration-200 ${
                      formData.targetRoles.includes(option.value)
                        ? 'bg-stone-900 text-white border-stone-900'
                        : 'bg-white text-stone-500 border-stone-200 hover:border-stone-400'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {submitStatus === 'error' && (
              <p className="text-sm text-red-500">{errorMessage}</p>
            )}

            <div className="pt-2">
              <Button
                type="submit"
                className="w-full bg-stone-900 hover:bg-stone-800 text-white rounded-full h-11"
                disabled={isSubmitting}
                loading={isSubmitting}
              >
                {isSubmitting ? 'Creating...' : 'Create Account'}
              </Button>
            </div>

            <p className="text-xs text-stone-400 text-center">
              By registering, you agree to our{' '}
              <Link href="/privacy" className="text-stone-500 hover:text-stone-900">
                Privacy Policy
              </Link>
            </p>
          </form>

          <p className="mt-8 text-center text-sm text-stone-400">
            Already have an account?{' '}
            <Link href="/candidate/login" className="text-stone-900 hover:text-stone-600">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </main>
  )
}
