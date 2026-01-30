'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DashboardNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import { talentPoolApi, employerApi, type TalentProfileDetail, type MatchStatus } from '@/lib/api'

// Use the TalentProfileDetail type from API
type TalentProfile = TalentProfileDetail & {
  candidate: TalentProfileDetail['candidate'] & {
    resumeData?: {
      name?: string
      email?: string
      phone?: string
      location?: string
      summary?: string
      skills?: string[]
      experience?: Array<{
        company: string
        title: string
        startDate?: string
        endDate?: string
        description?: string
        highlights?: string[]
      }>
      education?: Array<{
        institution: string
        degree?: string
        fieldOfStudy?: string
        startDate?: string
        endDate?: string
      }>
    }
  }
}

const STATUS_OPTIONS: { value: MatchStatus; label: string; color: string }[] = [
  { value: 'PENDING', label: 'Pending', color: 'bg-warm-100 text-warm-700' },
  { value: 'CONTACTED', label: 'Contacted', color: 'bg-blue-100 text-blue-700' },
  { value: 'IN_REVIEW', label: 'In Review', color: 'bg-yellow-100 text-yellow-700' },
  { value: 'SHORTLISTED', label: 'Shortlisted', color: 'bg-green-100 text-green-700' },
  { value: 'REJECTED', label: 'Rejected', color: 'bg-red-100 text-red-700' },
  { value: 'HIRED', label: 'Hired', color: 'bg-brand-100 text-brand-700' },
]

const SCORING_DIMENSIONS = [
  { key: 'communication', label: '沟通能力', labelEn: 'Communication' },
  { key: 'problemSolving', label: '解决问题', labelEn: 'Problem Solving' },
  { key: 'domainKnowledge', label: '专业知识', labelEn: 'Domain Knowledge' },
  { key: 'motivation', label: '动机', labelEn: 'Motivation' },
  { key: 'cultureFit', label: '文化契合', labelEn: 'Culture Fit' },
]

const VERTICAL_NAMES: Record<string, string> = {
  new_energy: '新能源 / 电动汽车',
  sales: '销售 / 商务拓展',
}

const ROLE_NAMES: Record<string, string> = {
  battery_engineer: '电池工程师',
  embedded_software: '嵌入式软件',
  autonomous_driving: '自动驾驶',
  supply_chain: '供应链',
  ev_sales: '新能源销售',
  sales_rep: '销售代表',
  bd_manager: '商务拓展',
  account_manager: '客户经理',
}

export default function TalentProfilePage() {
  const router = useRouter()
  const params = useParams()
  const profileId = params.profileId as string

  const [isLoading, setIsLoading] = useState(true)
  const [profile, setProfile] = useState<TalentProfile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [companyName, setCompanyName] = useState<string>('')

  // Status tracking
  const [currentStatus, setCurrentStatus] = useState<MatchStatus>('PENDING')
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false)

  // Video playback
  const [activeVideoIndex, setActiveVideoIndex] = useState<number | null>(null)

  // Contact modal
  const [showContactModal, setShowContactModal] = useState(false)
  const [contactSubject, setContactSubject] = useState('')
  const [contactMessage, setContactMessage] = useState('')
  const [isSending, setIsSending] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('employer_token')
    if (!token) {
      router.push('/login')
      return
    }

    // Get company name
    employerApi.getMe().then(employer => {
      setCompanyName(employer.companyName || '')
    }).catch(() => {})

    fetchProfile()
  }, [profileId])

  const handleLogout = () => {
    localStorage.removeItem('employer_token')
    localStorage.removeItem('employer')
    router.push('/login')
  }

  const fetchProfile = async () => {
    setIsLoading(true)
    try {
      const data = await talentPoolApi.getProfile(profileId)
      setProfile(data as TalentProfile)
      // Set initial status from employer's match record
      if (data.employerStatus?.status) {
        setCurrentStatus(data.employerStatus.status)
      }
    } catch (err) {
      console.error('Failed to fetch profile:', err)
      setError('Failed to load candidate profile')
    } finally {
      setIsLoading(false)
    }
  }

  const handleStatusChange = async (newStatus: MatchStatus) => {
    setIsUpdatingStatus(true)
    try {
      await talentPoolApi.updateStatus(profileId, newStatus)
      setCurrentStatus(newStatus)
    } catch (err) {
      console.error('Failed to update status:', err)
      alert('Failed to update status. Please try again.')
    } finally {
      setIsUpdatingStatus(false)
    }
  }

  const openContactModal = () => {
    if (!profile) return
    setContactSubject(`Interview Opportunity at ${companyName}`)
    setContactMessage(`Dear ${profile.candidate.name},

We reviewed your profile on ZhiMian and were impressed by your qualifications.

We would like to discuss a potential opportunity with you. Would you be available for a conversation?

Best regards,
${companyName}`)
    setShowContactModal(true)
  }

  const sendContactEmail = async () => {
    if (!profile || !contactSubject.trim() || !contactMessage.trim()) return

    setIsSending(true)
    try {
      await talentPoolApi.contactCandidate(profileId, {
        subject: contactSubject,
        body: contactMessage,
        messageType: 'interview_invite',
      })
      alert(`Message sent to ${profile.candidate.name}!`)
      setShowContactModal(false)
      setCurrentStatus('CONTACTED')
    } catch (err) {
      console.error('Failed to send message:', err)
      alert('Failed to send message. Please try again.')
    } finally {
      setIsSending(false)
    }
  }

  if (isLoading) {
    return (
      <PageWrapper className="flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-warm-200 border-t-brand-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-warm-500 text-sm">Loading profile...</p>
        </div>
      </PageWrapper>
    )
  }

  if (error || !profile) {
    return (
      <PageWrapper>
        <DashboardNavbar companyName={companyName} onLogout={handleLogout} />
        <Container className="py-8 pt-24 flex items-center justify-center">
          <Card className="max-w-md">
            <CardContent className="py-8 text-center">
              <p className="text-red-600 mb-4">{error || 'Profile not found'}</p>
              <Link href="/dashboard/talent-pool">
                <Button>Back to Talent Pool</Button>
              </Link>
            </CardContent>
          </Card>
        </Container>
      </PageWrapper>
    )
  }

  const { candidate, interview } = profile
  const resumeData = candidate.resumeData

  return (
    <PageWrapper>
      <DashboardNavbar companyName={companyName} onLogout={handleLogout} />

      <Container className="py-8 pt-24 max-w-4xl">
        {/* Back Button */}
        <Link href="/dashboard/talent-pool" className="inline-flex items-center text-sm text-warm-600 hover:text-warm-900 mb-6">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Talent Pool
        </Link>

        {/* Profile Header */}
        <Card className="mb-6">
          <CardContent className="py-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-brand-500 to-brand-600 rounded-full flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">
                    {candidate.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-warm-900">{candidate.name}</h1>
                  <p className="text-warm-600">{candidate.email}</p>
                  {candidate.phone && (
                    <p className="text-warm-600">{candidate.phone}</p>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="text-4xl font-bold text-brand-600">
                  {profile.profile.bestScore?.toFixed(1)}
                </div>
                <div className="text-sm text-warm-500">Interview Score</div>
              </div>
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-warm-100">
              <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                profile.profile.vertical === 'new_energy'
                  ? 'bg-brand-100 text-brand-700'
                  : 'bg-blue-100 text-blue-700'
              }`}>
                {VERTICAL_NAMES[profile.profile.vertical] || profile.profile.vertical}
              </span>
              <span className="px-3 py-1 text-sm font-medium rounded-full bg-warm-100 text-warm-700">
                {ROLE_NAMES[profile.profile.roleType] || profile.profile.roleType}
              </span>
              {resumeData?.location && (
                <span className="px-3 py-1 text-sm rounded-full bg-warm-100 text-warm-600">
                  📍 {resumeData.location}
                </span>
              )}
            </div>

            {/* Status & Actions */}
            <div className="mt-4 pt-4 border-t border-warm-100 flex flex-wrap gap-3 items-center">
              {/* Status Dropdown */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-warm-600">Status:</span>
                <select
                  value={currentStatus}
                  onChange={(e) => handleStatusChange(e.target.value as MatchStatus)}
                  disabled={isUpdatingStatus}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border-0 cursor-pointer ${
                    STATUS_OPTIONS.find(s => s.value === currentStatus)?.color || 'bg-warm-100 text-warm-700'
                  }`}
                >
                  {STATUS_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                {isUpdatingStatus && (
                  <span className="w-4 h-4 border-2 border-warm-300 border-t-brand-500 rounded-full animate-spin" />
                )}
              </div>

              <div className="flex-1" />

              {/* Action Buttons */}
              <Button variant="brand" onClick={openContactModal}>
                Send Message
              </Button>
              <Button
                variant="outline"
                onClick={() => setActiveVideoIndex(0)}
                disabled={!profile?.interview?.responses?.length}
              >
                View Interview Recording
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Left Column - Resume */}
          <div className="md:col-span-2 space-y-6">
            {/* Summary */}
            {resumeData?.summary && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-warm-600 whitespace-pre-line">{resumeData.summary}</p>
                </CardContent>
              </Card>
            )}

            {/* Experience */}
            {resumeData?.experience && resumeData.experience.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Work Experience</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {resumeData.experience.map((exp, i) => (
                      <div key={i} className={i > 0 ? 'pt-4 border-t border-warm-100' : ''}>
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium text-warm-900">{exp.title}</h4>
                            <p className="text-warm-600">{exp.company}</p>
                          </div>
                          <p className="text-sm text-warm-500">
                            {exp.startDate} - {exp.endDate || 'Present'}
                          </p>
                        </div>
                        {exp.description && (
                          <p className="text-sm text-warm-600 mt-2">{exp.description}</p>
                        )}
                        {exp.highlights && exp.highlights.length > 0 && (
                          <ul className="mt-2 text-sm text-warm-600 list-disc list-inside">
                            {exp.highlights.map((h, j) => (
                              <li key={j}>{h}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Education */}
            {resumeData?.education && resumeData.education.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Education</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {resumeData.education.map((edu, i) => (
                      <div key={i} className={i > 0 ? 'pt-4 border-t border-warm-100' : ''}>
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium text-warm-900">{edu.institution}</h4>
                            <p className="text-warm-600">
                              {edu.degree} {edu.fieldOfStudy && `in ${edu.fieldOfStudy}`}
                            </p>
                          </div>
                          {edu.startDate && (
                            <p className="text-sm text-warm-500">
                              {edu.startDate} - {edu.endDate || 'Present'}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column - Skills & Interview */}
          <div className="space-y-6">
            {/* Skills */}
            {resumeData?.skills && resumeData.skills.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Skills</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {resumeData.skills.map((skill, i) => (
                      <span
                        key={i}
                        className="px-3 py-1 text-sm bg-warm-100 text-warm-700 rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Interview Details */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Interview Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-warm-600">Latest Score</span>
                    <span className="font-medium">{profile.profile.interviewScore?.toFixed(1)}/10</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-warm-600">Best Score</span>
                    <span className="font-medium text-brand-600">{profile.profile.bestScore?.toFixed(1)}/10</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-warm-600">Attempts</span>
                    <span className="font-medium">{profile.profile.attemptCount}/3</span>
                  </div>
                  {profile.profile.completedAt && (
                    <div className="flex justify-between">
                      <span className="text-warm-600">Completed</span>
                      <span className="font-medium">
                        {new Date(profile.profile.completedAt).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {interview?.aiSummary && (
                  <div className="mt-4 pt-4 border-t border-warm-100">
                    <h4 className="font-medium text-warm-900 mb-2">AI Summary</h4>
                    <p className="text-sm text-warm-600">{interview.aiSummary}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Interview Responses with Videos */}
        {interview?.responses && interview.responses.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="text-lg">Interview Responses</CardTitle>
              <CardDescription>
                {interview.responses.length} question{interview.responses.length !== 1 ? 's' : ''} answered
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {interview.responses.map((response, index) => (
                  <div key={response.id} className={index > 0 ? 'pt-6 border-t border-warm-100' : ''}>
                    <div className="flex items-start gap-4">
                      {/* Question Number */}
                      <div className="flex-shrink-0 w-8 h-8 bg-brand-100 text-brand-700 rounded-full flex items-center justify-center font-medium text-sm">
                        {response.questionIndex + 1}
                      </div>

                      <div className="flex-1">
                        {/* Question Text */}
                        <h4 className="font-medium text-warm-900 mb-2">{response.questionText}</h4>

                        {/* Video Player */}
                        {response.videoUrl && (
                          <div className="mb-3">
                            {activeVideoIndex === index ? (
                              <div className="relative bg-black rounded-lg overflow-hidden">
                                <video
                                  src={response.videoUrl}
                                  controls
                                  autoPlay
                                  className="w-full max-h-[300px]"
                                  onEnded={() => setActiveVideoIndex(null)}
                                />
                                <button
                                  onClick={() => setActiveVideoIndex(null)}
                                  className="absolute top-2 right-2 p-1 bg-black/50 rounded-full text-white hover:bg-black/70"
                                >
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                  </svg>
                                </button>
                              </div>
                            ) : (
                              <button
                                onClick={() => setActiveVideoIndex(index)}
                                className="flex items-center gap-2 px-4 py-2 bg-warm-100 hover:bg-warm-200 rounded-lg text-warm-700 text-sm transition-colors"
                              >
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M8 5v14l11-7z" />
                                </svg>
                                Play Video ({response.durationSeconds ? `${Math.floor(response.durationSeconds / 60)}:${(response.durationSeconds % 60).toString().padStart(2, '0')}` : 'N/A'})
                              </button>
                            )}
                          </div>
                        )}

                        {/* Transcription */}
                        {response.transcription && (
                          <div className="mb-3 p-3 bg-warm-50 rounded-lg">
                            <p className="text-sm text-warm-700 italic">"{response.transcription}"</p>
                          </div>
                        )}

                        {/* Score & Analysis */}
                        <div className="flex items-start gap-4">
                          {/* Overall Score */}
                          <div className="text-center">
                            <div className="text-2xl font-bold text-brand-600">
                              {response.aiScore?.toFixed(1) || '-'}
                            </div>
                            <div className="text-xs text-warm-500">Score</div>
                          </div>

                          {/* Scoring Dimensions */}
                          {response.scoringDimensions && (
                            <div className="flex-1 grid grid-cols-5 gap-2">
                              {SCORING_DIMENSIONS.map(dim => {
                                const score = response.scoringDimensions?.[dim.key as keyof typeof response.scoringDimensions]
                                return (
                                  <div key={dim.key} className="text-center">
                                    <div className="text-sm font-medium text-warm-900">
                                      {score?.toFixed(1) || '-'}
                                    </div>
                                    <div className="text-xs text-warm-500">{dim.label}</div>
                                  </div>
                                )
                              })}
                            </div>
                          )}
                        </div>

                        {/* AI Analysis */}
                        {response.aiAnalysis && (
                          <p className="mt-2 text-sm text-warm-600">{response.aiAnalysis}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </Container>

      {/* Contact Modal */}
      {showContactModal && profile && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Contact {profile.candidate.name}</span>
                <button
                  onClick={() => setShowContactModal(false)}
                  className="text-warm-400 hover:text-warm-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </CardTitle>
              <CardDescription>
                Send an email to {profile.candidate.email}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Subject
                </label>
                <input
                  type="text"
                  value={contactSubject}
                  onChange={(e) => setContactSubject(e.target.value)}
                  className="w-full px-3 py-2 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                  placeholder="Email subject..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-warm-700 mb-1">
                  Message
                </label>
                <textarea
                  value={contactMessage}
                  onChange={(e) => setContactMessage(e.target.value)}
                  rows={8}
                  className="w-full px-3 py-2 border border-warm-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 resize-none"
                  placeholder="Write your message..."
                />
              </div>
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowContactModal(false)}
                  disabled={isSending}
                >
                  Cancel
                </Button>
                <Button
                  variant="brand"
                  className="flex-1"
                  onClick={sendContactEmail}
                  disabled={isSending || !contactSubject.trim() || !contactMessage.trim()}
                >
                  {isSending ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Sending...
                    </>
                  ) : (
                    'Send Email'
                  )}
                </Button>
              </div>
              <p className="text-xs text-warm-500 text-center">
                The candidate will receive this email and their status will be updated to "Contacted"
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </PageWrapper>
  )
}
