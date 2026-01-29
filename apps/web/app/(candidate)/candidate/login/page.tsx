'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function CandidateLoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // Look up candidate by email via local API route
      const response = await fetch(`/api/candidates/lookup?email=${encodeURIComponent(email)}`)

      if (!response.ok) {
        throw new Error('Failed to find account')
      }

      const data = await response.json()

      if (!data.candidates || data.candidates.length === 0) {
        throw new Error('No account found with this email. Please register first.')
      }

      const candidate = data.candidates[0]

      // Store candidate info
      localStorage.setItem('candidate', JSON.stringify({
        id: candidate.id,
        name: candidate.name,
        email: candidate.email,
      }))

      // Redirect to candidate dashboard
      router.push('/candidate/dashboard')

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setIsLoading(false)
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
          <CardTitle className="text-2xl">Welcome Back</CardTitle>
          <CardDescription>
            Sign in to continue your job search
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <Button
              type="submit"
              disabled={isLoading || !email}
              className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">或使用以下方式登录</span>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            className="w-full border-green-500 text-green-600 hover:bg-green-50"
            onClick={() => window.location.href = '/api/auth/wechat'}
          >
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 01.213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.328.328 0 00.186-.059l2.114-1.225a.866.866 0 01.627-.097c.853.186 1.753.282 2.697.282 4.801 0 8.692-3.288 8.692-7.342 0-4.054-3.89-7.343-8.692-7.343zm-3.16 5.06c.579 0 1.05.47 1.05 1.05 0 .58-.471 1.05-1.05 1.05-.58 0-1.05-.47-1.05-1.05 0-.58.47-1.05 1.05-1.05zm6.32 0c.58 0 1.05.47 1.05 1.05 0 .58-.47 1.05-1.05 1.05-.58 0-1.05-.47-1.05-1.05 0-.58.47-1.05 1.05-1.05zm4.632 8.358c0 3.324-3.193 6.022-7.13 6.022a8.79 8.79 0 01-2.213-.282.712.712 0 00-.515.08l-1.733 1.005a.27.27 0 01-.153.049.242.242 0 01-.238-.242c0-.059.024-.118.04-.175l.32-1.215a.484.484 0 00-.175-.546c-1.503-1.106-2.463-2.74-2.463-4.55 0-.508.073-1.001.204-1.47a9.158 9.158 0 003.627.742c.106 0 .21-.003.314-.01.03.337.088.669.175.994.016.058.036.115.054.172.018.058.038.115.06.171.021.057.045.113.07.168.025.055.053.109.083.162.03.053.062.105.096.156.034.051.07.1.109.149.039.048.08.095.123.14.043.045.088.089.136.13.047.042.097.082.148.12.052.038.106.074.162.108.056.034.114.066.174.096.06.03.121.057.184.082.063.025.128.047.194.067.066.02.133.037.202.052.068.014.138.026.208.034.071.008.142.013.214.015.072.002.145 0 .217-.005a2.35 2.35 0 00.428-.076l.112-.032a2.35 2.35 0 00.316-.126l.09-.045.003-.001a2.354 2.354 0 00.263-.166l.072-.054.002-.002c.076-.06.148-.125.216-.194l.05-.053.002-.002a2.36 2.36 0 00.157-.191l.04-.055a2.36 2.36 0 00.21-.379l.02-.044a2.36 2.36 0 00.127-.42l.007-.037c.031-.175.047-.354.047-.536 0-.076-.003-.151-.008-.226l-.002-.027a2.359 2.359 0 00-.046-.318l-.01-.043a2.363 2.363 0 00-.086-.29l-.017-.045a2.363 2.363 0 00-.123-.272l-.023-.044a2.36 2.36 0 00-.157-.254l-.028-.041a2.365 2.365 0 00-.186-.23l-.033-.037a2.365 2.365 0 00-.211-.203l-.037-.032a2.368 2.368 0 00-.233-.173l-.04-.027a2.37 2.37 0 00-.252-.144l-.04-.02a2.376 2.376 0 00-.267-.113l-.036-.013a2.38 2.38 0 00-.278-.081l-.03-.007a2.385 2.385 0 00-.285-.049l-.021-.002a2.395 2.395 0 00-.288-.016c-.033 0-.066 0-.099.002l-.012.001c-.097.004-.193.015-.287.033l-.003.001c3.165-1.02 5.43-3.534 5.43-6.504 0-.237-.02-.471-.051-.702z"/>
            </svg>
            微信登录 (WeChat Login)
          </Button>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              Don&apos;t have an account?{' '}
              <Link href="/candidate/register" className="text-emerald-600 hover:underline">
                Start your interview
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </main>
  )
}
