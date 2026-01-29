'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const targetRoleOptions = [
  { value: 'battery_engineer', label: 'Battery Engineer' },
  { value: 'embedded_software', label: 'Embedded Software' },
  { value: 'autonomous_driving', label: 'Autonomous Driving' },
  { value: 'supply_chain', label: 'Supply Chain' },
  { value: 'ev_sales', label: 'EV Sales' },
  { value: 'sales_rep', label: 'Sales Representative' },
  { value: 'bd_manager', label: 'BD Manager' },
  { value: 'account_manager', label: 'Account Manager' },
]

export default function CandidateRegisterPage() {
  const router = useRouter()
  const [step, setStep] = useState<'info' | 'roles'>('info')
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    targetRoles: [] as string[],
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
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

  const validateStep1 = () => {
    const newErrors: Record<string, string> = {}
    if (!formData.name.trim()) newErrors.name = 'Name is required'
    if (!formData.email.trim()) newErrors.email = 'Email is required'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format'
    }
    if (!formData.phone.trim()) newErrors.phone = 'Phone is required'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validateStep1()) {
      setStep('roles')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitError('')
    setIsSubmitting(true)

    try {
      // Register the candidate
      const response = await fetch('/api/candidates/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (!response.ok) {
        // Handle validation errors with details
        if (data.details && Array.isArray(data.details)) {
          const messages = data.details.map((d: { message?: string; path?: string[] }) => {
            const field = d.path?.[0] || 'field'
            return `${field}: ${d.message || 'Invalid'}`
          }).join('; ')
          throw new Error(messages)
        }
        throw new Error(data.error || 'Registration failed')
      }

      // Store candidate info in localStorage for the interview
      localStorage.setItem('candidate', JSON.stringify({
        id: data.candidate.id,
        name: data.candidate.name,
        email: data.candidate.email,
      }))

      // Start an interview session via local API route
      const interviewResponse = await fetch('/api/interviews/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: data.candidate.id,
        }),
      })

      if (!interviewResponse.ok) {
        // If no job exists or error, redirect to dashboard
        router.push('/candidate/dashboard')
        return
      }

      const interviewData = await interviewResponse.json()

      // Redirect to interview room
      router.push(`/interview/${interviewData.session_id}`)

    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Something went wrong')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-emerald-50 to-white flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <Link href="/" className="inline-flex items-center justify-center gap-2 mb-4">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold">智</span>
            </div>
          </Link>
          <CardTitle className="text-2xl">Start Your AI Interview</CardTitle>
          <CardDescription>
            {step === 'info'
              ? 'Create your profile to begin'
              : 'Select the roles you\'re interested in'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Progress indicator */}
          <div className="flex items-center gap-2 mb-6">
            <div className={`flex-1 h-1 rounded-full ${step === 'info' ? 'bg-emerald-600' : 'bg-emerald-600'}`} />
            <div className={`flex-1 h-1 rounded-full ${step === 'roles' ? 'bg-emerald-600' : 'bg-gray-200'}`} />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {step === 'info' && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name <span className="text-red-500">*</span></Label>
                  <Input
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    placeholder="Your name"
                    className={errors.name ? 'border-red-500' : ''}
                  />
                  {errors.name && <p className="text-sm text-red-500">{errors.name}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email <span className="text-red-500">*</span></Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="you@example.com"
                    className={errors.email ? 'border-red-500' : ''}
                  />
                  {errors.email && <p className="text-sm text-red-500">{errors.email}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number <span className="text-red-500">*</span></Label>
                  <Input
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="Your phone number"
                    className={errors.phone ? 'border-red-500' : ''}
                  />
                  {errors.phone && <p className="text-sm text-red-500">{errors.phone}</p>}
                </div>

                <Button
                  type="button"
                  onClick={handleNext}
                  className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
                >
                  Continue
                </Button>
              </>
            )}

            {step === 'roles' && (
              <>
                <div className="space-y-2">
                  <Label>What roles are you interested in?</Label>
                  <div className="flex flex-wrap gap-2">
                    {targetRoleOptions.map(option => (
                      <button
                        key={option.value}
                        type="button"
                        onClick={() => handleRoleToggle(option.value)}
                        className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                          formData.targetRoles.includes(option.value)
                            ? 'bg-emerald-600 text-white border-emerald-600'
                            : 'bg-white text-gray-700 border-gray-300 hover:border-emerald-400'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                  <p className="text-sm text-gray-500">Select at least one role</p>
                </div>

                {submitError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-sm text-red-600">{submitError}</p>
                  </div>
                )}

                <div className="flex gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setStep('info')}
                    className="flex-1"
                  >
                    Back
                  </Button>
                  <Button
                    type="submit"
                    disabled={isSubmitting || formData.targetRoles.length === 0}
                    className="flex-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
                  >
                    {isSubmitting ? 'Starting...' : 'Start Interview'}
                  </Button>
                </div>
              </>
            )}
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link href="/candidate/login" className="text-emerald-600 hover:underline">
              Sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  )
}
