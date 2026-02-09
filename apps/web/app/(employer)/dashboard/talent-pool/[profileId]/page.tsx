'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DashboardNavbar } from '@/components/layout/navbar'
import { Container, PageWrapper } from '@/components/layout/container'
import { talentPoolApi, employerApi, employerCalendarApi, type TalentProfileDetail, type MatchStatus, type CalendarStatus, type Job } from '@/lib/api'
import { ScheduleInterviewModal } from '@/components/employer/schedule-interview-modal'
import { GrowthTimeline } from '@/components/employer/growth-timeline'

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
  { value: 'PENDING', label: 'Pending', color: 'bg-gray-100 text-gray-700' },
  { value: 'CONTACTED', label: 'Contacted', color: 'bg-blue-100 text-blue-700' },
  { value: 'IN_REVIEW', label: 'In Review', color: 'bg-yellow-100 text-yellow-700' },
  { value: 'SHORTLISTED', label: 'Shortlisted', color: 'bg-green-100 text-green-700' },
  { value: 'REJECTED', label: 'Rejected', color: 'bg-red-100 text-red-700' },
  { value: 'HIRED', label: 'Hired', color: 'bg-teal-100 text-teal-700' },
]

const SCORING_DIMENSIONS = [
  { key: 'communication', label: 'Communication' },
  { key: 'problemSolving', label: 'Problem Solving' },
  { key: 'technicalKnowledge', label: 'Technical' },
  { key: 'growthMindset', label: 'Growth' },
  { key: 'cultureFit', label: 'Culture Fit' },
]

const VERTICAL_NAMES: Record<string, string> = {
  software_engineering: 'Software Engineering',
  engineering: 'Software Engineering',
  data: 'Data & Analytics',
  product: 'Product Management',
  business: 'Business & Product',
  design: 'Design',
  finance: 'Finance & IB',
}

const ROLE_NAMES: Record<string, string> = {
  // Software Engineering
  software_engineer: 'Software Engineer',
  embedded_engineer: 'Embedded Engineer',
  qa_engineer: 'QA Engineer',
  // Legacy engineering roles
  frontend_engineer: 'Frontend Engineer',
  backend_engineer: 'Backend Engineer',
  fullstack_engineer: 'Full Stack Engineer',
  mobile_engineer: 'Mobile Engineer',
  devops_engineer: 'DevOps Engineer',
  // Data
  data_analyst: 'Data Analyst',
  data_scientist: 'Data Scientist',
  ml_engineer: 'ML Engineer',
  data_engineer: 'Data Engineer',
  // Product
  product_manager: 'Product Manager',
  associate_pm: 'Associate PM',
  business_analyst: 'Business Analyst',
  // Design
  ux_designer: 'UX Designer',
  ui_designer: 'UI Designer',
  product_designer: 'Product Designer',
  // Finance
  ib_analyst: 'IB Analyst',
  finance_analyst: 'Finance Analyst',
  equity_research: 'Equity Research',
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

  // Calendar/scheduling state
  const [calendarStatus, setCalendarStatus] = useState<CalendarStatus | null>(null)
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [jobs, setJobs] = useState<Job[]>([])
  const [showCalendarPrompt, setShowCalendarPrompt] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('employer_token')
    if (!token) {
      router.push('/employer/login')
      return
    }

    // Get company name and jobs
    employerApi.getMe().then(employer => {
      setCompanyName(employer.companyName || '')
    }).catch(() => {})

    // Get calendar status
    employerCalendarApi.getStatus().then(status => {
      setCalendarStatus(status)
    }).catch(() => {
      setCalendarStatus({ connected: false })
    })

    // Get jobs for scheduling
    employerApi.listJobs(true).then(result => {
      setJobs(result.jobs)
    }).catch(() => {})

    fetchProfile()
  }, [profileId])

  const handleLogout = () => {
    localStorage.removeItem('employer_token')
    localStorage.removeItem('employer')
    router.push('/employer/login')
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

We reviewed your profile on Pathway and were impressed by your qualifications.

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
          <div className="w-12 h-12 border-2 border-gray-200 border-t-teal-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500 text-sm">Loading profile...</p>
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
              <Link href="/dashboard?tab=talent">
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
        <Link href="/dashboard?tab=talent" className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-6">
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
                <div className="w-16 h-16 bg-gradient-to-br from-teal-600 to-teal-500 rounded-full flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">
                    {candidate.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{candidate.name}</h1>
                  <p className="text-gray-600">{candidate.email}</p>
                  {candidate.phone && (
                    <p className="text-gray-600">{candidate.phone}</p>
                  )}
                </div>
              </div>
              <div className="text-right">
                {profile.profile.bestScore ? (
                  <>
                    <div className="text-4xl font-bold text-teal-600">
                      {profile.profile.bestScore.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-500">Interview Score</div>
                  </>
                ) : profile.profileScore ? (
                  <>
                    <div className="text-4xl font-bold text-blue-600">
                      {profile.profileScore.score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-500">Profile Score</div>
                  </>
                ) : (
                  <div className="text-sm text-gray-400">No score yet</div>
                )}
              </div>
            </div>

            {/* Completion Status */}
            {profile.completionStatus && (
              <div className="flex flex-wrap gap-2 mt-4">
                {profile.completionStatus.interviewCompleted && (
                  <span className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-full flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Interview Completed
                  </span>
                )}
                {!profile.completionStatus.interviewCompleted && (
                  <span className="px-3 py-1 text-sm bg-yellow-100 text-yellow-700 rounded-full">
                    No Interview Yet
                  </span>
                )}
                {profile.completionStatus.resumeUploaded && (
                  <span className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-full">
                    Resume Uploaded
                  </span>
                )}
                {profile.completionStatus.githubConnected && (
                  <span className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-full">
                    GitHub Connected
                  </span>
                )}
                {profile.completionStatus.educationFilled && (
                  <span className="px-3 py-1 text-sm bg-amber-100 text-amber-700 rounded-full">
                    Education Filled
                  </span>
                )}
              </div>
            )}

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-gray-100">
              {profile.profile.vertical && (
                <span className={`px-3 py-1 text-sm font-medium rounded-full ${
                  profile.profile.vertical === 'software_engineering' || profile.profile.vertical === 'engineering'
                    ? 'bg-teal-100 text-teal-700'
                    : profile.profile.vertical === 'data'
                    ? 'bg-teal-100 text-teal-600'
                    : profile.profile.vertical === 'product' || profile.profile.vertical === 'business'
                    ? 'bg-green-100 text-green-700'
                    : profile.profile.vertical === 'finance'
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-blue-100 text-blue-700'
                }`}>
                  {VERTICAL_NAMES[profile.profile.vertical] || profile.profile.vertical}
                </span>
              )}
              {profile.profile.roleType && (
                <span className="px-3 py-1 text-sm font-medium rounded-full bg-gray-100 text-gray-700">
                  {ROLE_NAMES[profile.profile.roleType] || profile.profile.roleType}
                </span>
              )}
              {resumeData?.location && (
                <span className="px-3 py-1 text-sm rounded-full bg-gray-100 text-gray-600">
                  📍 {resumeData.location}
                </span>
              )}
            </div>

            {/* Status & Actions */}
            <div className="mt-4 pt-4 border-t border-gray-100 flex flex-wrap gap-3 items-center">
              {/* Status Dropdown */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Status:</span>
                <select
                  value={currentStatus}
                  onChange={(e) => handleStatusChange(e.target.value as MatchStatus)}
                  disabled={isUpdatingStatus}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border-0 cursor-pointer ${
                    STATUS_OPTIONS.find(s => s.value === currentStatus)?.color || 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {STATUS_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
                {isUpdatingStatus && (
                  <span className="w-4 h-4 border-2 border-gray-300 border-t-teal-500 rounded-full animate-spin" />
                )}
              </div>

              <div className="flex-1" />

              {/* Action Buttons */}
              <Button
                variant="default"
                onClick={() => {
                  if (calendarStatus?.connected) {
                    setShowScheduleModal(true)
                  } else {
                    setShowCalendarPrompt(true)
                  }
                }}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Schedule Interview
              </Button>
              <Button variant="outline" onClick={openContactModal}>
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
                  <p className="text-gray-600 whitespace-pre-line">{resumeData.summary}</p>
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
                      <div key={i} className={i > 0 ? 'pt-4 border-t border-gray-100' : ''}>
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900">{exp.title}</h4>
                            <p className="text-gray-600">{exp.company}</p>
                          </div>
                          <p className="text-sm text-gray-500">
                            {exp.startDate} - {exp.endDate || 'Present'}
                          </p>
                        </div>
                        {exp.description && (
                          <p className="text-sm text-gray-600 mt-2">{exp.description}</p>
                        )}
                        {exp.highlights && exp.highlights.length > 0 && (
                          <ul className="mt-2 text-sm text-gray-600 list-disc list-inside">
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
                      <div key={i} className={i > 0 ? 'pt-4 border-t border-gray-100' : ''}>
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900">{edu.institution}</h4>
                            <p className="text-gray-600">
                              {edu.degree} {edu.fieldOfStudy && `in ${edu.fieldOfStudy}`}
                            </p>
                          </div>
                          {edu.startDate && (
                            <p className="text-sm text-gray-500">
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
                        className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* GitHub Profile */}
            {candidate.githubUsername && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                    </svg>
                    GitHub
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <a
                      href={`https://github.com/${candidate.githubUsername}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-teal-600 hover:underline font-medium"
                    >
                      @{candidate.githubUsername}
                    </a>
                    {candidate.githubData && (
                      <>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Public Repos</span>
                          <span className="font-medium">{candidate.githubData.publicRepos || candidate.githubData.repos?.length || 0}</span>
                        </div>
                        {candidate.githubData.totalContributions && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Contributions</span>
                            <span className="font-medium">{candidate.githubData.totalContributions}</span>
                          </div>
                        )}
                        {candidate.githubData.languages && Object.keys(candidate.githubData.languages).length > 0 && (
                          <div className="mt-2">
                            <span className="text-sm text-gray-600">Top Languages</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {Object.keys(candidate.githubData.languages).slice(0, 5).map(lang => (
                                <span key={lang} className="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded">
                                  {lang}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Growth Timeline - Shows candidate progress over time */}
            <Card>
              <CardContent className="py-4">
                <GrowthTimeline
                  candidateId={candidate.id}
                  profileId={profile.profile.id}
                />
              </CardContent>
            </Card>

            {/* Profile Score Breakdown (for candidates without interviews) */}
            {profile.profileScore && !profile.profile.bestScore && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Profile Score Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {profile.profileScore.breakdown.technicalSkills && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Technical Skills</span>
                        <span className="font-medium">{profile.profileScore.breakdown.technicalSkills.toFixed(1)}/10</span>
                      </div>
                    )}
                    {profile.profileScore.breakdown.experienceQuality && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Experience</span>
                        <span className="font-medium">{profile.profileScore.breakdown.experienceQuality.toFixed(1)}/10</span>
                      </div>
                    )}
                    {profile.profileScore.breakdown.education && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Education</span>
                        <span className="font-medium">{profile.profileScore.breakdown.education.toFixed(1)}/10</span>
                      </div>
                    )}
                    {profile.profileScore.breakdown.githubActivity && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">GitHub Activity</span>
                        <span className="font-medium">{profile.profileScore.breakdown.githubActivity.toFixed(1)}/10</span>
                      </div>
                    )}
                    <div className="pt-2 border-t border-gray-100 flex justify-between">
                      <span className="text-gray-900 font-medium">Overall</span>
                      <span className="font-bold text-blue-600">{profile.profileScore.score.toFixed(1)}/10</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-3">
                    This score is based on resume, GitHub, and education data. Interview score will be available after the candidate completes an interview.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Interview Details */}
            {(profile.profile.interviewScore || profile.profile.bestScore || interview) && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Interview Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {profile.profile.interviewScore && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Latest Score</span>
                      <span className="font-medium">{profile.profile.interviewScore.toFixed(1)}/10</span>
                    </div>
                  )}
                  {profile.profile.bestScore && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Best Score</span>
                      <span className="font-medium text-teal-600">{profile.profile.bestScore.toFixed(1)}/10</span>
                    </div>
                  )}
                  {profile.profile.totalInterviews !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Attempts</span>
                      <span className="font-medium">{profile.profile.totalInterviews}</span>
                    </div>
                  )}
                  {profile.profile.completedAt && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Completed</span>
                      <span className="font-medium">
                        {new Date(profile.profile.completedAt).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {interview?.aiSummary && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <h4 className="font-medium text-gray-900 mb-2">AI Summary</h4>
                    <p className="text-sm text-gray-600">{interview.aiSummary}</p>
                  </div>
                )}
              </CardContent>
            </Card>
            )}
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
                  <div key={response.id} className={index > 0 ? 'pt-6 border-t border-gray-100' : ''}>
                    <div className="flex items-start gap-4">
                      {/* Question Number */}
                      <div className="flex-shrink-0 w-8 h-8 bg-teal-100 text-teal-700 rounded-full flex items-center justify-center font-medium text-sm">
                        {response.questionIndex + 1}
                      </div>

                      <div className="flex-1">
                        {/* Question Text */}
                        <h4 className="font-medium text-gray-900 mb-2">{response.questionText}</h4>

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
                                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 text-sm transition-colors"
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
                          <div className="mb-3 p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-700 italic">"{response.transcription}"</p>
                          </div>
                        )}

                        {/* Score & Analysis */}
                        <div className="flex items-start gap-4">
                          {/* Overall Score */}
                          <div className="text-center">
                            <div className="text-2xl font-bold text-teal-600">
                              {response.aiScore?.toFixed(1) || '-'}
                            </div>
                            <div className="text-xs text-gray-500">Score</div>
                          </div>

                          {/* Scoring Dimensions */}
                          {response.scoringDimensions && (
                            <div className="flex-1 grid grid-cols-5 gap-2">
                              {SCORING_DIMENSIONS.map(dim => {
                                const score = response.scoringDimensions?.[dim.key as keyof typeof response.scoringDimensions]
                                return (
                                  <div key={dim.key} className="text-center">
                                    <div className="text-sm font-medium text-gray-900">
                                      {score?.toFixed(1) || '-'}
                                    </div>
                                    <div className="text-xs text-gray-500">{dim.label}</div>
                                  </div>
                                )
                              })}
                            </div>
                          )}
                        </div>

                        {/* AI Analysis */}
                        {response.aiAnalysis && (
                          <p className="mt-2 text-sm text-gray-600">{response.aiAnalysis}</p>
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
                  className="text-gray-400 hover:text-gray-600"
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
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subject
                </label>
                <input
                  type="text"
                  value={contactSubject}
                  onChange={(e) => setContactSubject(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
                  placeholder="Email subject..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Message
                </label>
                <textarea
                  value={contactMessage}
                  onChange={(e) => setContactMessage(e.target.value)}
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none"
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
                  variant="default"
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
              <p className="text-xs text-gray-500 text-center">
                The candidate will receive this email and their status will be updated to "Contacted"
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Schedule Interview Modal */}
      {showScheduleModal && profile && (
        <ScheduleInterviewModal
          candidateId={profile.candidate.id}
          candidateName={profile.candidate.name}
          candidateEmail={profile.candidate.email}
          jobs={jobs}
          onClose={() => setShowScheduleModal(false)}
          onSuccess={() => {
            // Optionally update status to CONTACTED
            if (currentStatus === 'PENDING') {
              handleStatusChange('CONTACTED')
            }
          }}
        />
      )}

      {/* Calendar Connection Prompt */}
      {showCalendarPrompt && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <svg className="w-6 h-6 text-teal-600" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11zM9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm-8 4H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/>
                </svg>
                Connect Google Calendar
              </CardTitle>
              <CardDescription>
                To schedule interviews, you need to connect your Google Calendar first.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-stone-50 rounded-lg p-4">
                <ul className="text-sm text-stone-600 space-y-2">
                  <li className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Events appear on your Google Calendar
                  </li>
                  <li className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Google Meet links generated automatically
                  </li>
                  <li className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-teal-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Candidates receive calendar invites instantly
                  </li>
                </ul>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowCalendarPrompt(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="default"
                  className="flex-1"
                  onClick={async () => {
                    try {
                      const { url, state } = await employerCalendarApi.getGoogleAuthUrl()
                      sessionStorage.setItem('employer_google_oauth_state', state)
                      window.location.href = url
                    } catch {
                      alert('Failed to start Google authorization. Please try again.')
                    }
                  }}
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  Connect Calendar
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </PageWrapper>
  )
}
