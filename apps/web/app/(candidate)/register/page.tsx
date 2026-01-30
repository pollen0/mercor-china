'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { candidateRegistrationSchema, targetRoleOptions, type CandidateRegistrationInput } from '@/lib/validations/candidate'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type FormErrors = Partial<Record<keyof CandidateRegistrationInput, string>>

function WeChatButton() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleWeChatLogin = async () => {
    setError('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/candidates/auth/wechat/url`)

      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        throw new Error(data.detail || '微信登录暂不可用')
      }

      const data = await response.json()

      // Store state for CSRF validation
      sessionStorage.setItem('wechat_oauth_state', data.state)

      // Redirect to WeChat authorization page
      window.location.href = data.auth_url
    } catch (err) {
      setError(err instanceof Error ? err.message : 'WeChat login failed')
      setIsLoading(false)
    }
  }

  return (
    <div>
      <Button
        type="button"
        variant="outline"
        className="w-full border-[#07C160] text-[#07C160] hover:bg-[#07C160]/10"
        onClick={handleWeChatLogin}
        disabled={isLoading}
      >
        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
          <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.27-.027-.407-.032zm-2.53 3.274c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.969-.982z"/>
        </svg>
        {isLoading ? '正在跳转...' : '使用微信快速注册'}
      </Button>
      {error && (
        <p className="mt-2 text-sm text-error text-center">{error}</p>
      )}
    </div>
  )
}

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState<CandidateRegistrationInput>({
    name: '',
    email: '',
    phone: '',
    password: '',
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
              Next step: Upload your resume to get personalized interview questions.
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
          {/* WeChat Registration Button */}
          <WeChatButton />

          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-warm-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-warm-500">或填写表单注册</span>
            </div>
          </div>

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

            <div className="space-y-2">
              <Label htmlFor="password">
                Password <span className="text-error">*</span>
              </Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="At least 8 characters with letters and numbers"
                className={errors.password ? 'border-error focus-visible:ring-error' : ''}
              />
              {errors.password && (
                <p className="text-sm text-error">{errors.password}</p>
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

            <p className="text-xs text-warm-500 text-center">
              By registering, you agree to our{' '}
              <Link href="/privacy" className="text-brand-600 hover:underline">
                Privacy Policy
              </Link>
              {' '}/ 注册即表示您同意我们的
              <Link href="/privacy" className="text-brand-600 hover:underline">
                隐私政策
              </Link>
            </p>

            <Button
              type="submit"
              variant="brand"
              className="w-full"
              disabled={isSubmitting}
              loading={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Register Now'}
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
