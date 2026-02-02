'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { candidateRegistrationSchema, targetRoleOptions, universityOptions, graduationYearOptions, type CandidateRegistrationInput } from '@/lib/validations/candidate'

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
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})
    setSubmitStatus('idle')
    setErrorMessage('')

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
      const response = await fetch('/api/candidates/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result.data),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Registration failed. Please try again.')
      }

      // Store candidate info and token
      localStorage.setItem('candidate', JSON.stringify({
        id: data.candidate.id,
        name: data.candidate.name,
        email: data.candidate.email,
      }))
      localStorage.setItem('candidate_token', data.token)

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

            <div className="grid grid-cols-2 gap-3">
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

              <div className="space-y-1.5">
                <Label htmlFor="major" className="text-stone-600 text-sm">Major</Label>
                <Input
                  id="major"
                  name="major"
                  value={formData.major || ''}
                  onChange={handleInputChange}
                  placeholder="CS"
                  className="border-stone-200 focus:border-stone-400 focus:ring-0"
                />
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
