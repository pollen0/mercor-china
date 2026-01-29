'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { candidateRegistrationSchema, targetRoleOptions, type CandidateRegistrationInput } from '@/lib/validations/candidate'

type FormErrors = Partial<Record<keyof CandidateRegistrationInput, string>>

export default function RegisterPage() {
  const [formData, setFormData] = useState<CandidateRegistrationInput>({
    name: '',
    email: '',
    phone: '',
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
        throw new Error(data.error || 'Registration failed. Please try again.')
      }

      setSubmitStatus('success')
      setFormData({ name: '', email: '', phone: '', targetRoles: [] })
    } catch (error) {
      setSubmitStatus('error')
      setErrorMessage(error instanceof Error ? error.message : 'Registration failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (submitStatus === 'success') {
    return (
      <main className="min-h-screen bg-gradient-to-b from-brand-50 to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md border-0 shadow-soft-lg">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-success-light rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <CardTitle className="text-success">Registration Successful!</CardTitle>
            <CardDescription>
              Thank you for registering. We will contact you soon.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Link href="/">
              <Button variant="outline">Back to Home</Button>
            </Link>
          </CardContent>
        </Card>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-brand-50 to-white flex items-center justify-center p-4">
      <Card className="w-full max-w-md border-0 shadow-soft-lg">
        <CardHeader className="text-center">
          <Link href="/" className="inline-flex items-center gap-2 justify-center mb-4 group">
            <div className="w-10 h-10 bg-gradient-to-br from-brand-500 to-brand-600 rounded-xl flex items-center justify-center shadow-brand group-hover:shadow-brand-lg transition-shadow">
              <span className="text-white font-bold">智</span>
            </div>
            <span className="text-xl font-semibold text-warm-900">ZhiMian 智面</span>
          </Link>
          <CardTitle>Candidate Registration</CardTitle>
          <CardDescription>
            Fill in your details to start your AI-powered job search
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="name">
                Full Name <span className="text-error">*</span>
              </Label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter your full name"
                className={errors.name ? 'border-error focus-visible:ring-error' : ''}
              />
              {errors.name && (
                <p className="text-sm text-error">{errors.name}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">
                Email <span className="text-error">*</span>
              </Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="example@email.com"
                className={errors.email ? 'border-error focus-visible:ring-error' : ''}
              />
              {errors.email && (
                <p className="text-sm text-error">{errors.email}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">
                Phone Number <span className="text-error">*</span>
              </Label>
              <Input
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="Enter your phone number"
                className={errors.phone ? 'border-error focus-visible:ring-error' : ''}
              />
              {errors.phone && (
                <p className="text-sm text-error">{errors.phone}</p>
              )}
            </div>

            <div className="space-y-3">
              <Label>Target Roles (select multiple)</Label>
              <div className="flex flex-wrap gap-2">
                {targetRoleOptions.map(option => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => handleRoleToggle(option.value)}
                    className={`px-4 py-2 text-sm rounded-full border-2 transition-all duration-200 font-medium ${
                      formData.targetRoles.includes(option.value)
                        ? 'bg-brand-500 text-white border-brand-500 shadow-brand'
                        : 'bg-white text-warm-700 border-warm-200 hover:border-brand-300 hover:text-brand-700'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {submitStatus === 'error' && (
              <div className="p-4 bg-error-light border border-error/20 rounded-xl">
                <p className="text-sm text-error-dark">{errorMessage}</p>
              </div>
            )}

            <Button
              type="submit"
              variant="brand"
              className="w-full"
              disabled={isSubmitting}
              loading={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Register Now'}
            </Button>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-warm-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-warm-500">或使用以下方式注册</span>
              </div>
            </div>

            <Button
              type="button"
              variant="outline"
              className="w-full border-green-500 text-green-600 hover:bg-green-50"
              onClick={() => window.location.href = '/api/auth/wechat'}
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 01.213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.328.328 0 00.186-.059l2.114-1.225a.866.866 0 01.627-.097c.853.186 1.753.282 2.697.282 4.801 0 8.692-3.288 8.692-7.342 0-4.054-3.89-7.343-8.692-7.343zm-3.16 5.06c.579 0 1.05.47 1.05 1.05 0 .58-.471 1.05-1.05 1.05-.58 0-1.05-.47-1.05-1.05 0-.58.47-1.05 1.05-1.05zm6.32 0c.58 0 1.05.47 1.05 1.05 0 .58-.47 1.05-1.05 1.05-.58 0-1.05-.47-1.05-1.05 0-.58.47-1.05 1.05-1.05z"/>
              </svg>
              微信快速注册 (WeChat Quick Register)
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-warm-500">
            Already have an account?{' '}
            <Link href="/candidate/login" className="text-brand-600 hover:text-brand-700 font-medium">
              Sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  )
}
