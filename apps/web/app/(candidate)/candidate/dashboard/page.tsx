'use client'

import { useEffect, useState, useCallback, memo, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Suspense } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { UploadProgress } from '@/components/ui/upload-progress'
import { DocumentPreview } from '@/components/ui/document-preview'
import { candidateApi, transformParsedResume, type GitHubData, type GitHubAnalysis as GitHubAnalysisType, type Activity as ApiActivity, type Award as ApiAward } from '@/lib/api'
import { useDashboardData, useSkillGap } from '@/lib/hooks/use-candidate-data'
import { EmailVerificationBanner } from '@/components/verification/email-verification-banner'
import { logout, clearAuthTokens } from '@/lib/auth'

interface Candidate {
  id: string
  name: string
  email: string
  token?: string
}

// Use API types for activities and awards (synced to backend)
type Activity = ApiActivity
type Award = ApiAward

const VERTICAL_CONFIG: Record<string, { name: string; icon: string }> = {
  software_engineering: { name: 'Software Engineering', icon: '💻' },
  data: { name: 'Data', icon: '📊' },
  product: { name: 'Product', icon: '📱' },
  design: { name: 'Design', icon: '🎨' },
  finance: { name: 'Finance', icon: '💰' },
}

const ROLE_NAMES: Record<string, string> = {
  // Software Engineering
  software_engineer: 'Software Engineer',
  embedded_engineer: 'Embedded Engineer',
  qa_engineer: 'QA Engineer',
  // Data
  data_analyst: 'Data Analyst',
  data_scientist: 'Data Scientist',
  ml_engineer: 'ML Engineer',
  data_engineer: 'Data Engineer',
  // Product
  product_manager: 'Product Manager',
  associate_pm: 'Associate PM',
  // Design
  ux_designer: 'UX Designer',
  ui_designer: 'UI Designer',
  product_designer: 'Product Designer',
  // Finance
  ib_analyst: 'IB Analyst',
  finance_analyst: 'Finance Analyst',
  equity_research: 'Equity Research',
}

// GitHub icon component
function GitHubIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
    </svg>
  )
}

function DashboardContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const initialTab = searchParams.get('tab') || 'profile'

  const [activeTab, setActiveTab] = useState<'profile' | 'interviews'>(initialTab as 'profile' | 'interviews')
  const [showProfileDropdown, setShowProfileDropdown] = useState(false)
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [activities, setActivities] = useState<Activity[]>([])
  const [awards, setAwards] = useState<Award[]>([])
  const [optedInToSharing, setOptedInToSharing] = useState<boolean | null>(null)
  const [showOptInBanner, setShowOptInBanner] = useState(false)

  // Use SWR hooks for data caching
  const {
    resumeData,
    githubData,
    githubAnalysis,
    verticalProfiles,
    matchingJobs,
    emailVerified,
    isLoading: isDataLoading,
    mutateCandidate,
    mutateResume,
    mutateGitHub,
  } = useDashboardData(token)

  // Skill gap fetched separately to avoid TypeScript inference depth limits
  const { skillGap } = useSkillGap(token)

  // Upload states
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadFileName, setUploadFileName] = useState<string>('')
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  // Document preview states
  const [previewDocument, setPreviewDocument] = useState<{ url: string; fileName: string } | null>(null)
  const [isConnectingGitHub, setIsConnectingGitHub] = useState(false)
  const [isRefreshingGitHub, setIsRefreshingGitHub] = useState(false)
  const [showReposDropdown, setShowReposDropdown] = useState(false)
  const [isUploadingTranscript, setIsUploadingTranscript] = useState(false)
  const [transcriptProgress, setTranscriptProgress] = useState(0)
  const [transcriptFileName, setTranscriptFileName] = useState<string>('')
  const [transcriptError, setTranscriptError] = useState<string | null>(null)
  const [isDraggingTranscript, setIsDraggingTranscript] = useState(false)
  const [transcriptData, setTranscriptData] = useState<{
    fileName: string
    uploadedAt: string
    courses?: string[]
    transcriptUrl?: string
    transcriptKey?: string
    verification?: {
      status: 'verified' | 'warning' | 'suspicious'
      confidenceScore: number
      summary: string
      flags?: Array<{
        code: string
        severity: 'high' | 'medium' | 'low'
        message: string
      }>
    }
  } | null>(null)
  const [isLoadingTranscriptUrl, setIsLoadingTranscriptUrl] = useState(false)
  const [showTranscriptDeleteConfirm, setShowTranscriptDeleteConfirm] = useState(false)
  const [githubError, setGithubError] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  // File input refs
  const resumeInputRef = useRef<HTMLInputElement>(null)
  const transcriptInputRef = useRef<HTMLInputElement>(null)

  // Activity/Award editing
  const [editingActivity, setEditingActivity] = useState<Activity | null>(null)
  const [editingAward, setEditingAward] = useState<Award | null>(null)
  const [showActivityForm, setShowActivityForm] = useState(false)
  const [showAwardForm, setShowAwardForm] = useState(false)

  // Auth check effect
  useEffect(() => {
    const stored = localStorage.getItem('candidate')
    const storedToken = localStorage.getItem('candidate_token')
    if (!stored || !storedToken) {
      router.push('/candidate/login')
      return
    }

    const candidateInfo = JSON.parse(stored)
    setCandidate({ ...candidateInfo, token: storedToken })
    setToken(storedToken)

    // Load transcript from localStorage (activities and awards now use API)
    const storedTranscript = localStorage.getItem(`transcript_${candidateInfo.id}`)
    if (storedTranscript) setTranscriptData(JSON.parse(storedTranscript))
  }, [router])

  // Re-fetch candidate profile when tab becomes visible (e.g. after email verification in another tab)
  useEffect(() => {
    if (emailVerified) return // Already verified, no need to listen
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        mutateCandidate()
      }
    }
    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange)
  }, [emailVerified, mutateCandidate])

  // Fetch activities and awards from API
  useEffect(() => {
    const fetchActivitiesAndAwards = async () => {
      if (!token) return

      try {
        const [activitiesData, awardsData] = await Promise.all([
          candidateApi.getActivities(token),
          candidateApi.getAwards(token),
        ])
        setActivities(activitiesData)
        setAwards(awardsData)
      } catch (error) {
        console.error('Failed to fetch activities/awards:', error)
      }
    }

    fetchActivitiesAndAwards()
  }, [token])

  // Fetch sharing preferences to show opt-in banner
  useEffect(() => {
    const fetchSharingPreferences = async () => {
      if (!token) return

      try {
        const prefs = await candidateApi.getSharingPreferences(token)
        setOptedInToSharing(prefs.optedInToSharing)
        setShowOptInBanner(!prefs.optedInToSharing)
      } catch (error) {
        console.error('Failed to fetch sharing preferences:', error)
      }
    }

    fetchSharingPreferences()
  }, [token])

  const isLoading = !token || isDataLoading

  const handleLogout = async () => {
    // Call server to invalidate token, then clear local storage and cookies
    await logout('candidate', true)
    localStorage.removeItem('candidate')
    router.push('/')
  }

  // Resume handlers with progress tracking
  const handleFileUpload = async (file: File) => {
    if (!candidate || !token) return

    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!validTypes.includes(file.type)) {
      setUploadError('Please upload a PDF or DOCX file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File size must be less than 10MB')
      return
    }

    setIsUploading(true)
    setUploadProgress(0)
    setUploadFileName(file.name)
    setUploadError(null)

    // Use XMLHttpRequest for progress tracking
    const formData = new FormData()
    formData.append('file', file)

    const xhr = new XMLHttpRequest()
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        // Upload is 0-50%, processing is 50-100%
        const percentComplete = Math.round((event.loaded / event.total) * 50)
        setUploadProgress(percentComplete)
      }
    })

    xhr.addEventListener('load', async () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        // Simulate processing progress
        setUploadProgress(70)
        await new Promise(resolve => setTimeout(resolve, 300))
        setUploadProgress(90)
        await new Promise(resolve => setTimeout(resolve, 200))
        setUploadProgress(100)

        // Parse the upload response and update SWR cache with the data directly
        try {
          const uploadResult = JSON.parse(xhr.responseText)
          const resumeData = {
            candidateId: candidate.id,
            resumeUrl: uploadResult.resume_url,
            rawText: uploadResult.raw_text_preview,
            parsedData: transformParsedResume(uploadResult.parsed_data),
            uploadedAt: new Date().toISOString(),
          }
          // Optimistic update: set data immediately, then revalidate in background
          mutateResume(resumeData, { revalidate: true })

          // Re-fetch activities and awards (they may have been auto-populated from resume)
          try {
            const [activitiesData, awardsData] = await Promise.all([
              candidateApi.getActivities(token),
              candidateApi.getAwards(token),
            ])
            setActivities(activitiesData)
            setAwards(awardsData)
          } catch (err) {
            console.error('Failed to refresh activities/awards after resume upload:', err)
          }
        } catch {
          // Fallback to simple revalidation
          mutateResume()
        }

        await new Promise(resolve => setTimeout(resolve, 500))
        setIsUploading(false)
        setUploadProgress(0)
      } else {
        try {
          const error = JSON.parse(xhr.responseText)
          setUploadError(error.detail || 'Failed to upload resume')
        } catch {
          setUploadError('Failed to upload resume')
        }
        setIsUploading(false)
        setUploadProgress(0)
      }
    })

    xhr.addEventListener('error', () => {
      setUploadError('Network error. Please try again.')
      setIsUploading(false)
      setUploadProgress(0)
    })

    xhr.open('POST', `${apiUrl}/api/candidates/${candidate.id}/resume`)
    xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    xhr.send(formData)
  }

  const handleDeleteResume = async () => {
    if (!candidate || !token) return
    setIsDeleting(true)
    try {
      await candidateApi.deleteResume(token)
      // Revalidate SWR cache
      mutateResume()
      setShowDeleteConfirm(false)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to delete resume')
    } finally {
      setIsDeleting(false)
    }
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileUpload(file)
  }, [candidate, token])

  // GitHub handlers
  const handleConnectGitHub = async () => {
    setGithubError(null)
    setIsConnectingGitHub(true)
    try {
      const { authUrl, state } = await candidateApi.getGitHubAuthUrl()
      sessionStorage.setItem('github_oauth_state', state)
      window.location.href = authUrl
    } catch (error) {
      setGithubError(error instanceof Error ? error.message : 'Failed to connect GitHub')
      setIsConnectingGitHub(false)
    }
  }

  const handleDisconnectGitHub = async () => {
    try {
      await candidateApi.disconnectGitHub()
      // Revalidate SWR cache
      mutateGitHub()
    } catch (error) {
      setGithubError(error instanceof Error ? error.message : 'Failed to disconnect GitHub')
    }
  }

  const handleRefreshGitHub = async () => {
    setGithubError(null)
    setIsRefreshingGitHub(true)
    try {
      await candidateApi.refreshGitHubData()
      // Revalidate SWR cache to get the new data
      mutateGitHub()
    } catch (error) {
      setGithubError(error instanceof Error ? error.message : 'Failed to refresh GitHub data')
    } finally {
      setIsRefreshingGitHub(false)
    }
  }

  // Transcript handlers
  const handleTranscriptDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDraggingTranscript(true)
  }, [])

  const handleTranscriptDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDraggingTranscript(false)
  }, [])

  const handleTranscriptDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDraggingTranscript(false)
    const file = e.dataTransfer.files[0]
    if (file) handleTranscriptUpload(file)
  }, [candidate, token])

  const handleTranscriptUpload = async (file: File) => {
    if (!candidate || !token) return
    if (file.type !== 'application/pdf') {
      setTranscriptError('Please upload a PDF file')
      return
    }

    setIsUploadingTranscript(true)
    setTranscriptProgress(0)
    setTranscriptFileName(file.name)
    setTranscriptError(null)

    // Use XMLHttpRequest for progress tracking
    const formData = new FormData()
    formData.append('file', file)

    const xhr = new XMLHttpRequest()
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        // Upload is 0-40%, processing is 40-100% (transcript parsing takes longer)
        const percentComplete = Math.round((event.loaded / event.total) * 40)
        setTranscriptProgress(percentComplete)
      }
    })

    xhr.addEventListener('load', async () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        // Simulate longer processing progress for AI parsing
        setTranscriptProgress(50)
        await new Promise(resolve => setTimeout(resolve, 400))
        setTranscriptProgress(70)
        await new Promise(resolve => setTimeout(resolve, 400))
        setTranscriptProgress(90)
        await new Promise(resolve => setTimeout(resolve, 300))
        setTranscriptProgress(100)

        // Parse response to get transcript URL, key, and verification
        let transcriptUrl: string | undefined
        let transcriptKey: string | undefined
        let verification: typeof transcriptData extends null ? never : NonNullable<typeof transcriptData>['verification'] | undefined
        try {
          const response = JSON.parse(xhr.responseText)
          transcriptUrl = response.transcript_url
          transcriptKey = response.transcript_key
          // Parse verification response
          if (response.verification) {
            verification = {
              status: response.verification.status,
              confidenceScore: response.verification.confidence_score,
              summary: response.verification.summary,
              flags: response.verification.flags,
            }
          }
        } catch {
          // Response parsing failed, continue without URL
        }

        // Store transcript metadata in localStorage
        const transcriptInfo = {
          fileName: file.name,
          uploadedAt: new Date().toISOString(),
          courses: [] as string[],
          transcriptUrl,
          transcriptKey,
          verification,
        }
        setTranscriptData(transcriptInfo)
        localStorage.setItem(`transcript_${candidate.id}`, JSON.stringify(transcriptInfo))

        await new Promise(resolve => setTimeout(resolve, 500))
        setIsUploadingTranscript(false)
        setTranscriptProgress(0)
      } else {
        try {
          const error = JSON.parse(xhr.responseText)
          setTranscriptError(error.detail || 'Failed to upload transcript')
        } catch {
          setTranscriptError('Failed to upload transcript')
        }
        setIsUploadingTranscript(false)
        setTranscriptProgress(0)
      }
    })

    xhr.addEventListener('error', () => {
      setTranscriptError('Network error. Please try again.')
      setIsUploadingTranscript(false)
      setTranscriptProgress(0)
    })

    xhr.open('POST', `${apiUrl}/api/candidates/${candidate.id}/transcript`)
    xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    xhr.send(formData)
  }

  const handleDeleteTranscript = async () => {
    if (!candidate || !token) return

    try {
      // Call backend to delete transcript
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      await fetch(`${apiUrl}/api/candidates/me/transcript`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
    } catch (e) {
      console.error('Failed to delete transcript from server:', e)
    }

    localStorage.removeItem(`transcript_${candidate.id}`)
    setTranscriptData(null)
    setShowTranscriptDeleteConfirm(false)
  }

  const handlePreviewTranscript = async () => {
    if (!transcriptData || !token) return

    // If we have a stored URL, try to use it first
    if (transcriptData.transcriptUrl) {
      setPreviewDocument({
        url: transcriptData.transcriptUrl,
        fileName: transcriptData.fileName
      })
      return
    }

    // If we have a transcript key but no URL, fetch a fresh signed URL
    if (transcriptData.transcriptKey) {
      setIsLoadingTranscriptUrl(true)
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/candidates/me/transcript/url`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })

        if (response.ok) {
          const data = await response.json()
          // Update stored data with fresh URL
          const updatedData = { ...transcriptData, transcriptUrl: data.transcript_url }
          setTranscriptData(updatedData)
          if (candidate) {
            localStorage.setItem(`transcript_${candidate.id}`, JSON.stringify(updatedData))
          }
          setPreviewDocument({
            url: data.transcript_url,
            fileName: transcriptData.fileName
          })
        } else {
          setTranscriptError('Failed to load transcript preview')
        }
      } catch (e) {
        console.error('Failed to get transcript URL:', e)
        setTranscriptError('Failed to load transcript preview')
      } finally {
        setIsLoadingTranscriptUrl(false)
      }
    }
  }

  // Activity handlers (using API)
  const saveActivity = async (activity: Activity) => {
    if (!candidate || !token) return
    try {
      if (editingActivity) {
        // Update existing activity
        const updated = await candidateApi.updateActivity(activity.id, activity, token)
        setActivities(activities.map(a => a.id === activity.id ? updated : a))
      } else {
        // Create new activity
        const created = await candidateApi.createActivity(activity, token)
        setActivities([...activities, created])
      }
      setShowActivityForm(false)
      setEditingActivity(null)
    } catch (error) {
      console.error('Failed to save activity:', error)
    }
  }

  const deleteActivity = async (id: string) => {
    if (!candidate || !token) return
    try {
      await candidateApi.deleteActivity(id, token)
      setActivities(activities.filter(a => a.id !== id))
    } catch (error) {
      console.error('Failed to delete activity:', error)
    }
  }

  // Award handlers (using API)
  const saveAward = async (award: Award) => {
    if (!candidate || !token) return
    try {
      if (editingAward) {
        // Update existing award
        const updated = await candidateApi.updateAward(award.id, award, token)
        setAwards(awards.map(a => a.id === award.id ? updated : a))
      } else {
        // Create new award
        const created = await candidateApi.createAward(award, token)
        setAwards([...awards, created])
      }
      setShowAwardForm(false)
      setEditingAward(null)
    } catch (error) {
      console.error('Failed to save award:', error)
    }
  }

  const deleteAward = async (id: string) => {
    if (!candidate || !token) return
    try {
      await candidateApi.deleteAward(id, token)
      setAwards(awards.filter(a => a.id !== id))
    } catch (error) {
      console.error('Failed to delete award:', error)
    }
  }

  const getProfileForVertical = (vertical: string) => {
    return profiles.find(p => p.vertical === vertical)
  }

  const hasResume = resumeData?.parsedData != null
  const hasGitHub = githubData != null
  const profiles = verticalProfiles || []
  const jobs = matchingJobs || []
  const hasCompletedProfiles = profiles.some(p => p.status === 'completed')

  if (isLoading) {
    return (
      <main className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-stone-200 border-t-stone-900 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-stone-400 text-sm">Loading...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-100 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link href="/" className="text-lg font-semibold text-stone-900">
            Pathway
          </Link>
          <div className="flex items-center gap-4">
            {/* Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                className="flex items-center gap-2 px-3 py-1.5 bg-stone-100 hover:bg-stone-200 rounded-full transition-colors cursor-pointer"
              >
                <div className="w-6 h-6 bg-teal-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium text-xs">
                    {(candidate?.name?.charAt(0) || candidate?.email?.split('@')[0]?.charAt(0) || 'U').toUpperCase()}
                  </span>
                </div>
                <span className="text-sm text-stone-700 font-medium">{candidate?.name || candidate?.email?.split('@')[0]}</span>
                <svg className={`w-4 h-4 text-stone-400 transition-transform ${showProfileDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {showProfileDropdown && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setShowProfileDropdown(false)} />
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-stone-200 py-2 z-20">
                    {/* User Info */}
                    <div className="px-4 py-3 border-b border-stone-100">
                      <p className="font-medium text-stone-900">{candidate?.name || candidate?.email?.split('@')[0]}</p>
                      <p className="text-xs text-stone-500">{candidate?.email}</p>
                    </div>

                    {/* Menu Items */}
                    <div className="py-1">
                      <button
                        onClick={() => {
                          setShowProfileDropdown(false)
                          router.push('/candidate/settings')
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-stone-700 hover:bg-stone-50 flex items-center gap-3"
                      >
                        <svg className="w-4 h-4 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        Settings
                      </button>
                    </div>

                    {/* Logout */}
                    <div className="border-t border-stone-100 pt-1">
                      <button
                        onClick={() => {
                          setShowProfileDropdown(false)
                          handleLogout()
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-3"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        Logout
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-stone-100">
        <div className="max-w-4xl mx-auto px-6">
          <div className="flex gap-1">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors duration-200 ${
                activeTab === 'profile'
                  ? 'border-stone-900 text-stone-900'
                  : 'border-transparent text-stone-500 hover:text-stone-700'
              }`}
            >
              Profile
            </button>
            <button
              onClick={() => setActiveTab('interviews')}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors duration-200 ${
                activeTab === 'interviews'
                  ? 'border-stone-900 text-stone-900'
                  : 'border-transparent text-stone-500 hover:text-stone-700'
              }`}
            >
              Interviews
            </button>
          </div>
        </div>
      </div>

      {/* Opt-in Banner */}
      {showOptInBanner && (
        <div className="bg-gradient-to-r from-teal-600 to-teal-500 text-white">
          <div className="max-w-4xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex-1">
                <p className="font-semibold mb-1">Get matched with companies automatically</p>
                <p className="text-sm text-teal-100">
                  Opt in to profile sharing to let vetted employers discover you based on your skills and growth trajectory
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowOptInBanner(false)}
                  className="text-sm text-teal-100 hover:text-white underline"
                >
                  Dismiss
                </button>
                <Link href="/candidate/settings">
                  <Button
                    size="sm"
                    className="bg-white text-teal-600 hover:bg-teal-50 font-medium"
                  >
                    Enable Sharing
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Email Verification Banner */}
        {!emailVerified && candidate?.email && (
          <EmailVerificationBanner email={candidate.email} />
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="space-y-6">
            {/* Resume Section */}
            <Card>
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">Resume</CardTitle>
                    <CardDescription>Upload your resume (PDF, DOCX - Max 10MB)</CardDescription>
                  </div>
                  {hasResume && resumeData?.uploadedAt && (
                    <span className="text-xs text-gray-400">
                      Updated {new Date(resumeData.uploadedAt).toLocaleDateString()} at {new Date(resumeData.uploadedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-lg p-6 text-center transition-all ${
                    isDragging ? 'border-gray-400 bg-gray-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="w-10 h-10 mx-auto mb-3 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <p className="text-sm text-gray-500 mb-3">
                    {hasResume ? 'Drop a new file to replace' : 'Drag and drop your resume, or'}
                  </p>
                  <input
                    ref={resumeInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                    className="hidden"
                    disabled={isUploading}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={isUploading}
                    onClick={() => resumeInputRef.current?.click()}
                  >
                    {isUploading ? 'Uploading...' : hasResume ? 'Replace File' : 'Choose File'}
                  </Button>
                </div>

                {/* Upload Progress Bar */}
                <UploadProgress
                  progress={uploadProgress}
                  isUploading={isUploading}
                  fileName={uploadFileName}
                />

                {uploadError && <p className="mt-2 text-sm text-red-500">{uploadError}</p>}

                {/* Uploaded File Info */}
                {hasResume && resumeData?.resumeUrl && (
                  <div className="mt-3 flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-teal-100 rounded flex items-center justify-center">
                        <svg className="w-4 h-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {resumeData.parsedData?.name ? `${resumeData.parsedData.name}'s Resume` : 'Resume'}
                        </p>
                        {resumeData.uploadedAt && (
                          <p className="text-xs text-gray-500">
                            Uploaded {new Date(resumeData.uploadedAt).toLocaleDateString()} at {new Date(resumeData.uploadedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-teal-600 hover:text-teal-700 hover:bg-teal-50"
                        onClick={() => setPreviewDocument({
                          url: resumeData.resumeUrl!,
                          fileName: resumeData.parsedData?.name ? `${resumeData.parsedData.name}'s Resume` : 'Resume'
                        })}
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        Preview
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        onClick={() => setShowDeleteConfirm(true)}
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Delete
                      </Button>
                    </div>
                  </div>
                )}

                {/* Resume Preview - Full Parsed Data */}
                {resumeData?.parsedData && (
                  <div className="mt-4 space-y-4">
                    {/* Header */}
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="font-medium text-gray-900">{resumeData.parsedData.name || 'Resume'}</p>
                          {resumeData.parsedData.email && (
                            <p className="text-xs text-gray-500">{resumeData.parsedData.email}</p>
                          )}
                          {resumeData.parsedData.location && (
                            <p className="text-xs text-gray-400">{resumeData.parsedData.location}</p>
                          )}
                        </div>
                        <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">Parsed</Badge>
                      </div>
                      {resumeData.parsedData.summary && (
                        <p className="text-sm text-gray-600 mt-2">{resumeData.parsedData.summary}</p>
                      )}
                    </div>

                    {/* Education Section */}
                    {resumeData.parsedData.education && resumeData.parsedData.education.length > 0 && (
                      <div className="p-4 bg-white border border-gray-100 rounded-lg">
                        <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <svg className="w-4 h-4 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0v6m-9-5l9 5 9-5" />
                          </svg>
                          Education
                        </h4>
                        <div className="space-y-3">
                          {resumeData.parsedData.education.map((edu, i) => (
                            <div key={i} className="border-l-2 border-teal-100 pl-3">
                              <p className="font-medium text-gray-900 text-sm">{edu.institution}</p>
                              {edu.degree && (
                                <p className="text-sm text-gray-600">
                                  {edu.degree}{edu.fieldOfStudy ? ` in ${edu.fieldOfStudy}` : ''}
                                </p>
                              )}
                              <div className="flex items-center gap-3 text-xs text-gray-400 mt-0.5">
                                {edu.startDate && edu.endDate && (
                                  <span>{edu.startDate} - {edu.endDate}</span>
                                )}
                                {edu.gpa && (
                                  <span className="bg-teal-50 text-teal-700 px-1.5 py-0.5 rounded font-medium">
                                    GPA: {edu.gpa}
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Skills Section */}
                    {resumeData.parsedData.skills && resumeData.parsedData.skills.length > 0 && (
                      <div className="p-4 bg-white border border-gray-100 rounded-lg">
                        <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                          Skills
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {resumeData.parsedData.skills.map((skill, i) => (
                            <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Experience Section */}
                    {resumeData.parsedData.experience && resumeData.parsedData.experience.length > 0 && (
                      <div className="p-4 bg-white border border-gray-100 rounded-lg">
                        <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                          Experience
                        </h4>
                        <div className="space-y-4">
                          {resumeData.parsedData.experience.map((exp, i) => (
                            <div key={i} className="border-l-2 border-green-100 pl-3">
                              <p className="font-medium text-gray-900 text-sm">{exp.title}</p>
                              <p className="text-sm text-gray-600">{exp.company}</p>
                              {exp.startDate && (
                                <p className="text-xs text-gray-400">{exp.startDate} - {exp.endDate || 'Present'}</p>
                              )}
                              {exp.description && (
                                <p className="text-xs text-gray-500 mt-1">{exp.description}</p>
                              )}
                              {exp.highlights && exp.highlights.length > 0 && (
                                <ul className="mt-1 space-y-0.5">
                                  {exp.highlights.slice(0, 3).map((h, j) => (
                                    <li key={j} className="text-xs text-gray-500 flex items-start gap-1">
                                      <span className="text-green-400 mt-0.5">•</span>
                                      <span>{h}</span>
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Projects Section */}
                    {resumeData.parsedData.projects && resumeData.parsedData.projects.length > 0 && (
                      <div className="p-4 bg-white border border-gray-100 rounded-lg">
                        <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <svg className="w-4 h-4 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                          </svg>
                          Projects
                        </h4>
                        <div className="space-y-3">
                          {resumeData.parsedData.projects.map((proj, i) => (
                            <div key={i} className="border-l-2 border-teal-100 pl-3">
                              <p className="font-medium text-gray-900 text-sm">{proj.name}</p>
                              {proj.description && (
                                <p className="text-xs text-gray-500 mt-0.5">{proj.description}</p>
                              )}
                              {proj.technologies && proj.technologies.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {proj.technologies.map((tech, j) => (
                                    <span key={j} className="text-xs bg-teal-50 text-teal-600 px-1.5 py-0.5 rounded">
                                      {tech}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Languages & Certifications */}
                    {((resumeData.parsedData.languages && resumeData.parsedData.languages.length > 0) ||
                      (resumeData.parsedData.certifications && resumeData.parsedData.certifications.length > 0)) && (
                      <div className="p-4 bg-white border border-gray-100 rounded-lg">
                        <div className="grid grid-cols-2 gap-4">
                          {resumeData.parsedData.languages && resumeData.parsedData.languages.length > 0 && (
                            <div>
                              <h4 className="text-sm font-semibold text-gray-900 mb-2">Languages</h4>
                              <div className="flex flex-wrap gap-1">
                                {resumeData.parsedData.languages.map((lang, i) => (
                                  <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                                    {lang}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {resumeData.parsedData.certifications && resumeData.parsedData.certifications.length > 0 && (
                            <div>
                              <h4 className="text-sm font-semibold text-gray-900 mb-2">Certifications</h4>
                              <ul className="space-y-1">
                                {resumeData.parsedData.certifications.map((cert, i) => (
                                  <li key={i} className="text-xs text-gray-600 flex items-center gap-1">
                                    <svg className="w-3 h-3 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                    </svg>
                                    {cert}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* GitHub Section */}
            <Card>
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <GitHubIcon className="w-5 h-5" />
                      GitHub
                    </CardTitle>
                    <CardDescription>Connect your GitHub to showcase projects</CardDescription>
                  </div>
                  {hasGitHub && (
                    <div className="flex flex-col items-end gap-1">
                      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Connected</Badge>
                      {githubData?.repos?.[0]?.updatedAt && (
                        <span className="text-xs text-gray-400">
                          Last activity {new Date(githubData.repos[0].updatedAt).toLocaleDateString()} at {new Date(githubData.repos[0].updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {hasGitHub && githubData ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <div className="w-10 h-10 bg-gray-900 rounded-full flex items-center justify-center">
                        <GitHubIcon className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">@{githubData.username}</p>
                        <p className="text-xs text-gray-500">
                          {githubData.repos?.length || githubData.publicRepos || 0} repos · {githubData.followers || 0} followers
                        </p>
                      </div>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleRefreshGitHub}
                          disabled={isRefreshingGitHub}
                          className="text-gray-500 hover:text-teal-600"
                          title="Pull latest GitHub data"
                        >
                          <svg className={`w-4 h-4 ${isRefreshingGitHub ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                        </Button>
                        <Button variant="ghost" size="sm" onClick={handleDisconnectGitHub} className="text-gray-400">
                          Disconnect
                        </Button>
                      </div>
                    </div>

                    {/* Languages */}
                    {githubData.languages && Object.keys(githubData.languages).length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(githubData.languages).slice(0, 5).map(([lang]) => (
                          <span key={lang} className="text-xs bg-gray-100 px-2 py-0.5 rounded">{lang}</span>
                        ))}
                      </div>
                    )}

                    {/* Repos Dropdown */}
                    {githubData.repos && githubData.repos.length > 0 && (
                      <div className="border-t pt-3">
                        <button
                          onClick={() => setShowReposDropdown(!showReposDropdown)}
                          className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 hover:text-gray-900"
                        >
                          <span>Repositories ({githubData.repos.length})</span>
                          <svg
                            className={`w-4 h-4 transition-transform ${showReposDropdown ? 'rotate-180' : ''}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>

                        {showReposDropdown && (
                          <div className="mt-2 space-y-2 max-h-64 overflow-y-auto">
                            {githubData.repos.map((repo, idx: number) => (
                              <a
                                key={idx}
                                href={repo.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block p-2 rounded-lg border border-gray-100 hover:border-gray-200 hover:bg-gray-50 transition-colors"
                              >
                                <div className="flex items-start justify-between gap-2">
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                      <span className="font-medium text-sm text-gray-900 truncate">{repo.name}</span>
                                      {repo.isFork && (
                                        <span className="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">fork</span>
                                      )}
                                      {repo.isOwner === false && (
                                        <span className="text-xs px-1.5 py-0.5 bg-teal-50 text-teal-600 rounded">collaborator</span>
                                      )}
                                    </div>
                                    {repo.description && (
                                      <p className="text-xs text-gray-500 truncate mt-0.5">{repo.description}</p>
                                    )}
                                  </div>
                                  <div className="flex items-center gap-2 text-xs text-gray-400 flex-shrink-0">
                                    {repo.language && (
                                      <span className="px-1.5 py-0.5 bg-gray-100 rounded">{repo.language}</span>
                                    )}
                                    {repo.stars > 0 && (
                                      <span className="flex items-center gap-0.5">
                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                        </svg>
                                        {repo.stars}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </a>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* GitHub Analysis Results */}
                    {githubAnalysis && (
                      <div className="border-t pt-3 mt-3">
                        <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
                          <svg className="w-4 h-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                          </svg>
                          GitHub Analysis
                        </h4>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="p-2 bg-gray-50 rounded-lg text-center">
                            <p className="text-lg font-semibold text-teal-600">
                              {githubAnalysis.overallScore.toFixed(1)}
                            </p>
                            <p className="text-xs text-gray-500">Overall</p>
                          </div>
                          <div className="p-2 bg-gray-50 rounded-lg text-center">
                            <p className="text-lg font-semibold text-purple-600">
                              {githubAnalysis.originalityScore.toFixed(1)}
                            </p>
                            <p className="text-xs text-gray-500">Originality</p>
                          </div>
                          <div className="p-2 bg-gray-50 rounded-lg text-center">
                            <p className="text-lg font-semibold text-blue-600">
                              {githubAnalysis.activityScore.toFixed(1)}
                            </p>
                            <p className="text-xs text-gray-500">Activity</p>
                          </div>
                          <div className="p-2 bg-gray-50 rounded-lg text-center">
                            <p className="text-lg font-semibold text-amber-600">
                              {githubAnalysis.depthScore.toFixed(1)}
                            </p>
                            <p className="text-xs text-gray-500">Depth</p>
                          </div>
                        </div>
                        <div className="mt-2 p-2 bg-gray-50 rounded-lg text-center">
                          <p className="text-lg font-semibold text-green-600">
                            {githubAnalysis.collaborationScore.toFixed(1)}
                          </p>
                          <p className="text-xs text-gray-500">Collaboration</p>
                        </div>
                      </div>
                    )}

                  </div>
                ) : (
                  <div className="text-center py-4">
                    <Button
                      variant="outline"
                      onClick={handleConnectGitHub}
                      disabled={isConnectingGitHub}
                      className="border-gray-300"
                    >
                      <GitHubIcon className="w-4 h-4 mr-2" />
                      {isConnectingGitHub ? 'Connecting...' : 'Connect GitHub'}
                    </Button>
                  </div>
                )}
                {githubError && <p className="mt-2 text-sm text-red-500">{githubError}</p>}
              </CardContent>
            </Card>

            {/* Transcript Section */}
            <Card>
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">Unofficial Transcript</CardTitle>
                    <CardDescription>Upload your transcript to highlight coursework (PDF only)</CardDescription>
                  </div>
                  {transcriptData?.uploadedAt && (
                    <span className="text-xs text-gray-400">
                      Updated {new Date(transcriptData.uploadedAt).toLocaleDateString()} at {new Date(transcriptData.uploadedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div
                  onDragOver={handleTranscriptDragOver}
                  onDragLeave={handleTranscriptDragLeave}
                  onDrop={handleTranscriptDrop}
                  className={`border-2 border-dashed rounded-lg p-4 text-center transition-all ${
                    isDraggingTranscript ? 'border-gray-400 bg-gray-50' : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    ref={transcriptInputRef}
                    type="file"
                    accept=".pdf"
                    onChange={(e) => e.target.files?.[0] && handleTranscriptUpload(e.target.files[0])}
                    className="hidden"
                    disabled={isUploadingTranscript}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={isUploadingTranscript}
                    onClick={() => transcriptInputRef.current?.click()}
                  >
                    {isUploadingTranscript ? 'Uploading...' : transcriptData ? 'Replace Transcript' : 'Upload Transcript'}
                  </Button>
                </div>

                {/* Upload Progress Bar */}
                <UploadProgress
                  progress={transcriptProgress}
                  isUploading={isUploadingTranscript}
                  fileName={transcriptFileName}
                />

                {transcriptError && <p className="mt-2 text-sm text-red-500">{transcriptError}</p>}

                {/* Uploaded Transcript Info */}
                {transcriptData && (
                  <div className="mt-3 flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-emerald-100 rounded flex items-center justify-center">
                        <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0v6" />
                        </svg>
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium text-gray-900">
                            {transcriptData.fileName}
                          </p>
                          {/* Verification Badge */}
                          {transcriptData.verification && (
                            <span
                              className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                transcriptData.verification.status === 'verified'
                                  ? 'bg-teal-50 text-teal-700'
                                  : transcriptData.verification.status === 'warning'
                                  ? 'bg-amber-50 text-amber-700'
                                  : 'bg-red-50 text-red-700'
                              }`}
                              title={transcriptData.verification.summary}
                            >
                              {transcriptData.verification.status === 'verified' ? (
                                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              ) : transcriptData.verification.status === 'warning' ? (
                                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                              ) : (
                                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                              )}
                              {transcriptData.verification.status === 'verified'
                                ? 'Verified'
                                : transcriptData.verification.status === 'warning'
                                ? 'Review'
                                : 'Suspicious'}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500">
                          Uploaded {new Date(transcriptData.uploadedAt).toLocaleDateString()} at {new Date(transcriptData.uploadedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {(transcriptData.transcriptUrl || transcriptData.transcriptKey) && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                          onClick={handlePreviewTranscript}
                          disabled={isLoadingTranscriptUrl}
                        >
                          {isLoadingTranscriptUrl ? (
                            <div className="w-4 h-4 mr-1 border-2 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
                          ) : (
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                          )}
                          Preview
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        onClick={() => setShowTranscriptDeleteConfirm(true)}
                      >
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Delete
                      </Button>
                    </div>
                  </div>
                )}

                {/* Courses from Transcript */}
                {transcriptData?.courses && transcriptData.courses.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                      <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                      Extracted Courses ({transcriptData.courses.length})
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {transcriptData.courses.slice(0, 12).map((course, idx) => (
                        <span
                          key={idx}
                          className="text-xs px-2 py-1 bg-emerald-50 text-emerald-700 rounded-md border border-emerald-100"
                        >
                          {course}
                        </span>
                      ))}
                      {transcriptData.courses.length > 12 && (
                        <span className="text-xs px-2 py-1 text-gray-500">
                          +{transcriptData.courses.length - 12} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Activities Section */}
            <Card>
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">Activities & Leadership</CardTitle>
                    <CardDescription>Clubs, organizations, volunteer work, etc.</CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => { setShowActivityForm(true); setEditingActivity(null); }}
                  >
                    Add Activity
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {activities.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-4">No activities added yet</p>
                ) : (
                  <div className="space-y-3">
                    {activities.map((activity) => (
                      <div key={activity.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium text-gray-900">{activity.activityName}</p>
                            {activity.organization && <p className="text-sm text-gray-600">{activity.organization}</p>}
                            {activity.role && <p className="text-xs text-gray-500">{activity.role}</p>}
                            {activity.description && (
                              <p className="text-sm text-gray-500 mt-1">{activity.description}</p>
                            )}
                          </div>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => { setEditingActivity(activity); setShowActivityForm(true); }}
                              className="text-gray-400 h-8 w-8 p-0"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                              </svg>
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteActivity(activity.id)}
                              className="text-red-400 h-8 w-8 p-0"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Awards Section */}
            <Card>
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">Awards & Achievements</CardTitle>
                    <CardDescription>Honors, scholarships, competitions, certifications</CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => { setShowAwardForm(true); setEditingAward(null); }}
                  >
                    Add Award
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {awards.length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-4">No awards added yet</p>
                ) : (
                  <div className="space-y-3">
                    {awards.map((award) => (
                      <div key={award.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium text-gray-900">{award.name}</p>
                            {award.issuer && <p className="text-sm text-gray-600">{award.issuer}</p>}
                            {award.date && <p className="text-xs text-gray-500">{award.date}</p>}
                            {award.description && (
                              <p className="text-sm text-gray-500 mt-1">{award.description}</p>
                            )}
                          </div>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => { setEditingAward(award); setShowAwardForm(true); }}
                              className="text-gray-400 h-8 w-8 p-0"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                              </svg>
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteAward(award.id)}
                              className="text-red-400 h-8 w-8 p-0"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Skill Gap Analysis Section */}
            {skillGap && (
              <Card>
                <CardHeader className="pb-4">
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Skills Analysis
                    </CardTitle>
                    <CardDescription>AI-powered analysis of your skills based on your profile</CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Score Overview */}
                  <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg mb-4">
                    <div className="w-16 h-16 rounded-full bg-white shadow-sm flex items-center justify-center">
                      <span className="text-2xl font-bold text-indigo-600">
                        {skillGap.avgProficiencyScore?.toFixed(0) || '-'}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Proficiency Score</p>
                      <p className="text-sm text-gray-500">
                        Based on {skillGap.matchedRequirements || 0} skills analyzed
                      </p>
                    </div>
                  </div>

                  {/* Strongest Areas */}
                  {skillGap.strongestAreas && skillGap.strongestAreas.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Your Strengths
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {skillGap.strongestAreas.slice(0, 6).map((skill, idx) => (
                          <span
                            key={idx}
                            className="text-xs px-2 py-1 bg-green-50 text-green-700 rounded-md border border-green-100"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Bonus Skills */}
                  {skillGap.bonusSkills && skillGap.bonusSkills.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                        <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                        </svg>
                        Bonus Skills
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {skillGap.bonusSkills.slice(0, 6).map((skill, idx) => (
                          <span
                            key={idx}
                            className="text-xs px-2 py-1 bg-purple-50 text-purple-700 rounded-md border border-purple-100"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Areas for Growth */}
                  {skillGap.criticalGaps && skillGap.criticalGaps.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                        <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        Areas for Growth
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {skillGap.criticalGaps.slice(0, 6).map((skill, idx) => (
                          <span
                            key={idx}
                            className="text-xs px-2 py-1 bg-amber-50 text-amber-700 rounded-md border border-amber-100"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Learning Priorities */}
                  {skillGap.learningPriorities && skillGap.learningPriorities.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                        <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                        Recommended Learning
                      </h4>
                      <div className="space-y-2">
                        {skillGap.learningPriorities.slice(0, 3).map((item, idx) => (
                          <div
                            key={idx}
                            className="p-2 bg-gray-50 rounded-lg"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium text-gray-900">{item.skill}</span>
                              <span className={`text-xs px-1.5 py-0.5 rounded ${
                                item.priority === 'critical' ? 'bg-red-100 text-red-700' :
                                item.priority === 'recommended' ? 'bg-blue-100 text-blue-700' :
                                'bg-gray-100 text-gray-600'
                              }`}>
                                {item.priority}
                              </span>
                            </div>
                            <p className="text-xs text-gray-500 mt-1">{item.reason}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Interviews Tab */}
        {activeTab === 'interviews' && (
          <div className="space-y-8">
            {/* Interview Profiles */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">Your Interviews</h2>
                  <p className="text-sm text-gray-500">Complete interviews to join the talent pool</p>
                </div>
                <Link href="/interview/select">
                  <Button className="bg-gray-900 hover:bg-gray-800 text-white rounded-full px-4">
                    Start Interview
                  </Button>
                </Link>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                {Object.entries(VERTICAL_CONFIG).map(([key, config]) => {
                  const profile = getProfileForVertical(key)
                  const isCompleted = profile?.status === 'completed'
                  const isInProgress = profile?.status === 'in_progress'

                  return (
                    <Card key={key} className="border-stone-100 hover:border-stone-200 transition-all duration-300">
                      <CardContent className="p-5">
                        <div className="flex items-start justify-between mb-3">
                          <h3 className="font-medium text-stone-900">{config.name}</h3>
                          {isCompleted && (
                            <span className="text-xs text-stone-500 bg-stone-100 px-2 py-0.5 rounded-full">Done</span>
                          )}
                        </div>

                        {isCompleted ? (
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="text-stone-400">Role</span>
                              <span className="text-stone-700">{ROLE_NAMES[profile.roleType] || profile.roleType}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-stone-400">Score</span>
                              <span className="font-semibold text-stone-900">{profile.bestScore?.toFixed(1)}/10</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-stone-400">Interviews</span>
                              <span className="text-stone-700">{profile.totalInterviews}</span>
                            </div>
                            {profile.canInterview ? (
                              <Link href="/interview/select" className="block mt-3">
                                <Button variant="outline" size="sm" className="w-full border-stone-200 text-stone-600 hover:bg-stone-50">
                                  Retake Interview
                                </Button>
                              </Link>
                            ) : profile.nextEligibleAt ? (
                              <div className="mt-3 text-center">
                                <p className="text-xs text-stone-400">Retake available</p>
                                <p className="text-sm font-medium text-stone-600">
                                  {(() => {
                                    const now = new Date()
                                    const eligible = new Date(profile.nextEligibleAt)
                                    const diffMs = eligible.getTime() - now.getTime()
                                    const diffDays = Math.max(0, Math.ceil(diffMs / (1000 * 60 * 60 * 24)))
                                    return diffDays > 0 ? `in ${diffDays} day${diffDays !== 1 ? 's' : ''}` : 'now'
                                  })()}
                                </p>
                              </div>
                            ) : null}
                          </div>
                        ) : isInProgress ? (
                          <div className="text-center py-2">
                            <p className="text-amber-600/80 text-sm mb-2">In progress</p>
                            <Link href={profile?.interviewSessionId ? `/interview/${profile.interviewSessionId}` : '/interview/select'}>
                              <Button size="sm" className="bg-stone-900 hover:bg-stone-800 text-white rounded-full px-4">
                                Continue
                              </Button>
                            </Link>
                          </div>
                        ) : (
                          <div className="text-center py-2">
                            <p className="text-stone-300 text-sm mb-2">Not started</p>
                            <Link href="/interview/select">
                              <Button variant="ghost" size="sm" className="text-stone-500 hover:text-stone-900">
                                Start
                              </Button>
                            </Link>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </div>

            {/* Matching Jobs */}
            {hasCompletedProfiles && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Matching Opportunities ({jobs.length})
                </h2>

                {jobs.length === 0 ? (
                  <Card>
                    <CardContent className="py-8 text-center">
                      <p className="text-gray-400">No matches yet</p>
                      <p className="text-gray-300 text-sm">Employers will contact you when they find a match</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="grid sm:grid-cols-2 gap-4">
                    {jobs.map((job) => (
                      <Card key={job.jobId} className="hover:shadow-md transition-shadow">
                        <CardContent className="p-5">
                          <h3 className="font-medium text-gray-900 mb-1">{job.jobTitle}</h3>
                          <p className="text-sm text-gray-400 mb-3">{job.companyName}</p>
                          <div className="flex items-center gap-2 text-xs">
                            <span className="text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                              {VERTICAL_CONFIG[job.vertical as keyof typeof VERTICAL_CONFIG]?.name || job.vertical}
                            </span>
                            {job.matchScore && (
                              <span className="text-gray-700 font-medium">{job.matchScore.toFixed(0)}% match</span>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* How it works */}
            <Card className="bg-gray-50 border-gray-100">
              <CardContent className="py-6">
                <p className="text-xs text-gray-400 uppercase tracking-wide mb-3">How it works</p>
                <ul className="text-sm text-gray-600 space-y-2">
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
                    Complete one interview per vertical
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
                    Your profile is shown to all employers
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
                    Interview monthly to show your growth
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Delete Resume Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-red-600">Delete Resume?</CardTitle>
              <CardDescription>
                This will permanently delete your resume and parsed data.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex gap-3 justify-end">
              <Button variant="outline" onClick={() => setShowDeleteConfirm(false)} disabled={isDeleting}>
                Cancel
              </Button>
              <Button
                className="bg-red-600 hover:bg-red-700 text-white"
                onClick={handleDeleteResume}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Delete Transcript Confirmation Modal */}
      {showTranscriptDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-red-600">Delete Transcript?</CardTitle>
              <CardDescription>
                This will remove your transcript data.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex gap-3 justify-end">
              <Button variant="outline" onClick={() => setShowTranscriptDeleteConfirm(false)}>
                Cancel
              </Button>
              <Button
                className="bg-red-600 hover:bg-red-700 text-white"
                onClick={handleDeleteTranscript}
              >
                Delete
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Activity Form Modal */}
      {showActivityForm && (
        <ActivityFormModal
          activity={editingActivity}
          onSave={saveActivity}
          onClose={() => { setShowActivityForm(false); setEditingActivity(null); }}
        />
      )}

      {/* Award Form Modal */}
      {showAwardForm && (
        <AwardFormModal
          award={editingAward}
          onSave={saveAward}
          onClose={() => { setShowAwardForm(false); setEditingAward(null); }}
        />
      )}

      {/* Document Preview Modal */}
      {previewDocument && (
        <DocumentPreview
          url={previewDocument.url}
          fileName={previewDocument.fileName}
          onClose={() => setPreviewDocument(null)}
        />
      )}
    </main>
  )
}

// Activity Form Modal - Memoized to prevent unnecessary re-renders
const ActivityFormModal = memo(function ActivityFormModal({
  activity,
  onSave,
  onClose,
}: {
  activity: Activity | null
  onSave: (activity: Activity) => void
  onClose: () => void
}) {
  const [form, setForm] = useState<Activity>(
    activity || { id: '', activityName: '', organization: '', role: '', description: '' }
  )

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{activity ? 'Edit Activity' : 'Add Activity'}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="activityName">Activity/Organization Name *</Label>
            <Input
              id="activityName"
              value={form.activityName}
              onChange={(e) => setForm({ ...form, activityName: e.target.value })}
              placeholder="e.g., Computer Science Club"
            />
          </div>
          <div>
            <Label htmlFor="organization">Institution/Affiliation</Label>
            <Input
              id="organization"
              value={form.organization || ''}
              onChange={(e) => setForm({ ...form, organization: e.target.value })}
              placeholder="e.g., UC Berkeley"
            />
          </div>
          <div>
            <Label htmlFor="role">Your Role</Label>
            <Input
              id="role"
              value={form.role || ''}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
              placeholder="e.g., President, Member"
            />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              value={form.description || ''}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Brief description of your involvement..."
              className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm resize-none h-20"
            />
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <Button variant="outline" onClick={onClose}>Cancel</Button>
            <Button
              onClick={() => form.activityName && onSave(form)}
              disabled={!form.activityName}
              className="bg-gray-900 hover:bg-gray-800 text-white"
            >
              {activity ? 'Save Changes' : 'Add Activity'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
})

// Award Form Modal - Memoized to prevent unnecessary re-renders
const AwardFormModal = memo(function AwardFormModal({
  award,
  onSave,
  onClose,
}: {
  award: Award | null
  onSave: (award: Award) => void
  onClose: () => void
}) {
  const [form, setForm] = useState<Award>(
    award || { id: '', name: '', issuer: '', date: '', description: '' }
  )

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{award ? 'Edit Award' : 'Add Award'}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="name">Award/Achievement Name *</Label>
            <Input
              id="name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="e.g., Dean's List, Hackathon Winner"
            />
          </div>
          <div>
            <Label htmlFor="issuer">Issued By</Label>
            <Input
              id="issuer"
              value={form.issuer || ''}
              onChange={(e) => setForm({ ...form, issuer: e.target.value })}
              placeholder="e.g., Stanford University, MLH"
            />
          </div>
          <div>
            <Label htmlFor="date">Date</Label>
            <Input
              id="date"
              value={form.date || ''}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              placeholder="e.g., May 2024"
            />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <textarea
              id="description"
              value={form.description || ''}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Brief description..."
              className="w-full border border-gray-200 rounded-md px-3 py-2 text-sm resize-none h-20"
            />
          </div>
          <div className="flex gap-3 justify-end pt-2">
            <Button variant="outline" onClick={onClose}>Cancel</Button>
            <Button
              onClick={() => form.name && onSave(form)}
              disabled={!form.name}
              className="bg-gray-900 hover:bg-gray-800 text-white"
            >
              {award ? 'Save Changes' : 'Add Award'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
})

export default function CandidateDashboard() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-white flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
      </main>
    }>
      <DashboardContent />
    </Suspense>
  )
}
