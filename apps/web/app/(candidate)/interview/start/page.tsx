'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { inviteApi, type InviteValidation } from '@/lib/api'

function InterviewStartContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  const [validation, setValidation] = useState<InviteValidation | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Form state
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (!token) {
      setError('No invite token provided')
      setIsLoading(false)
      return
    }

    const validateToken = async () => {
      try {
        const result = await inviteApi.validate(token)
        setValidation(result)
        if (!result.valid) {
          setError(result.error || 'Invalid invite link')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to validate invite')
      } finally {
        setIsLoading(false)
      }
    }

    validateToken()
  }, [token])

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!name.trim()) {
      errors.name = 'Name is required'
    } else if (name.length < 2) {
      errors.name = 'Name must be at least 2 characters'
    }

    if (!email.trim()) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Please enter a valid email address'
    }

    if (!phone.trim()) {
      errors.phone = 'Phone number is required'
    } else if (!/^1[3-9]\d{9}$/.test(phone)) {
      errors.phone = 'Please enter a valid Chinese mobile number'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm() || !token) return

    setIsSubmitting(true)
    setError(null)

    try {
      const result = await inviteApi.registerAndStart({
        name,
        email,
        phone,
        inviteToken: token,
      })

      // Redirect to interview room
      router.push(`/interview/${result.sessionId}/room`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start interview')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Validating invite link...</p>
        </div>
      </main>
    )
  }

  if (error || !validation?.valid) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <CardTitle className="text-red-600">Invalid Invite Link</CardTitle>
            <CardDescription>
              {error || validation?.error || 'This invite link is not valid'}
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <p className="text-sm text-gray-500">
              Please contact the recruiter for a new invite link.
            </p>
            <Link href="/">
              <Button variant="outline">Go to Home</Button>
            </Link>
          </CardContent>
        </Card>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <Link href="/" className="text-2xl font-bold text-blue-600 mb-2">
            ZhiPin AI
          </Link>
          <CardTitle className="text-xl">Video Interview</CardTitle>
          <CardDescription>
            <span className="font-semibold text-gray-900">{validation.jobTitle}</span>
            <br />
            at {validation.companyName}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="bg-blue-50 rounded-lg p-4 mb-4">
              <h3 className="font-semibold text-blue-900 mb-2">Before you begin</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• This interview has 5 questions</li>
                <li>• You have up to 2 minutes per question</li>
                <li>• You can re-record before submitting</li>
                <li>• Make sure you have a working camera and microphone</li>
              </ul>
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">
                Full Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value)
                  if (formErrors.name) setFormErrors({ ...formErrors, name: '' })
                }}
                placeholder="Enter your full name"
                className={formErrors.name ? 'border-red-500' : ''}
              />
              {formErrors.name && (
                <p className="text-sm text-red-500">{formErrors.name}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">
                Email <span className="text-red-500">*</span>
              </Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  if (formErrors.email) setFormErrors({ ...formErrors, email: '' })
                }}
                placeholder="your.email@example.com"
                className={formErrors.email ? 'border-red-500' : ''}
              />
              {formErrors.email && (
                <p className="text-sm text-red-500">{formErrors.email}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">
                Phone Number <span className="text-red-500">*</span>
              </Label>
              <Input
                id="phone"
                value={phone}
                onChange={(e) => {
                  setPhone(e.target.value)
                  if (formErrors.phone) setFormErrors({ ...formErrors, phone: '' })
                }}
                placeholder="13800138000"
                className={formErrors.phone ? 'border-red-500' : ''}
              />
              {formErrors.phone && (
                <p className="text-sm text-red-500">{formErrors.phone}</p>
              )}
              <p className="text-xs text-gray-500">Enter your Chinese mobile number</p>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <Button
              type="submit"
              className="w-full"
              size="lg"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Starting Interview...' : 'Start Interview'}
            </Button>

            <p className="text-xs text-center text-gray-500">
              By starting this interview, you agree to have your video and audio
              recorded for evaluation purposes.
            </p>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}

export default function InterviewStartPage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </main>
    }>
      <InterviewStartContent />
    </Suspense>
  )
}
