'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { candidateApi, type ResumeResponse, type ParsedResumeData } from '@/lib/api'
import { Suspense } from 'react'

interface Candidate {
  id: string
  name: string
  email: string
  token?: string
}

function ResumePageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const isOnboarding = searchParams.get('onboarding') === 'true'
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [resumeData, setResumeData] = useState<ResumeResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [isStartingInterview, setIsStartingInterview] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('candidate')
    const token = localStorage.getItem('candidate_token')
    if (!stored) {
      router.push('/candidate/login')
      return
    }

    const candidateInfo = JSON.parse(stored)
    setCandidate({ ...candidateInfo, token })

    // Fetch existing resume
    const fetchResume = async () => {
      try {
        const resume = await candidateApi.getMyResume(token || undefined)
        setResumeData(resume)
      } catch {
        // No resume yet, that's fine
      } finally {
        setIsLoading(false)
      }
    }

    fetchResume()
  }, [router])

  const startInterview = async () => {
    if (!candidate) return
    setIsStartingInterview(true)

    try {
      const response = await fetch('/api/interviews/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: candidate.id,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to start interview')
      }

      const data = await response.json()
      router.push(`/interview/${data.session_id}`)
    } catch (error) {
      console.error('Failed to start interview:', error)
      alert(error instanceof Error ? error.message : 'Failed to start interview')
      setIsStartingInterview(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    if (!candidate) return

    // Validate file type
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!validTypes.includes(file.type)) {
      setUploadError('Please upload a PDF or DOCX file')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File size must be less than 10MB')
      return
    }

    setIsUploading(true)
    setUploadError(null)
    setUploadSuccess(false)

    try {
      const result = await candidateApi.uploadResume(candidate.id, file, candidate.token)
      if (result.success) {
        setUploadSuccess(true)
        // Refresh resume data
        const resume = await candidateApi.getMyResume(candidate.token)
        setResumeData(resume)
      }
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Failed to upload resume')
    } finally {
      setIsUploading(false)
    }
  }

  const handleDeleteResume = async () => {
    if (!candidate) return

    setIsDeleting(true)
    try {
      await candidateApi.deleteResume(candidate.token)
      setResumeData(null)
      setUploadSuccess(false)
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
    if (file) {
      handleFileUpload(file)
    }
  }, [candidate])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-brand-50 to-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600"></div>
      </main>
    )
  }

  const hasResume = resumeData?.parsedData != null

  return (
    <main className="min-h-screen bg-gradient-to-b from-brand-50 to-white">
      {/* Header */}
      <header className="bg-white border-b border-warm-200 shadow-soft">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Link href={isOnboarding ? "/" : "/candidate/dashboard"} className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-brand-500 to-brand-600 rounded-lg flex items-center justify-center shadow-brand">
                  <span className="text-white font-bold text-sm">智</span>
                </div>
                <span className="font-semibold text-warm-900">ZhiMian</span>
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-warm-600">Hi, {candidate?.name}</span>
              {!isOnboarding && (
                <Link href="/candidate/dashboard">
                  <Button variant="outline" size="sm">Back to Dashboard</Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Onboarding Progress */}
      {isOnboarding && (
        <div className="bg-brand-50 border-b border-brand-100">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-brand-600 text-white flex items-center justify-center text-sm font-medium">1</div>
                <span className="text-sm font-medium text-brand-700">Register</span>
              </div>
              <div className="w-12 h-0.5 bg-brand-300"></div>
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${hasResume ? 'bg-brand-600 text-white' : 'bg-brand-600 text-white ring-4 ring-brand-200'}`}>2</div>
                <span className="text-sm font-medium text-brand-700">Upload Resume</span>
              </div>
              <div className="w-12 h-0.5 bg-brand-200"></div>
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${hasResume ? 'bg-brand-200 text-brand-700' : 'bg-brand-100 text-brand-400'}`}>3</div>
                <span className={`text-sm font-medium ${hasResume ? 'text-brand-600' : 'text-brand-400'}`}>AI Interview</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-warm-900">
            {isOnboarding ? 'Upload Your Resume' : 'My Resume'}
          </h1>
          <p className="text-warm-600">
            {isOnboarding
              ? 'We\'ll use your resume to create personalized interview questions tailored to your experience.'
              : 'Upload your resume for AI-powered analysis and personalized interview questions'
            }
          </p>
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle className="text-error">Delete Resume?</CardTitle>
                <CardDescription>
                  This will permanently delete your resume and parsed data. You&apos;ll need to upload a new one before interviewing.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex gap-3 justify-end">
                <Button
                  variant="outline"
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isDeleting}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDeleteResume}
                  disabled={isDeleting}
                >
                  {isDeleting ? 'Deleting...' : 'Delete Resume'}
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Upload Section */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>{hasResume ? 'Replace Resume' : 'Upload Resume'}</CardTitle>
                <CardDescription>
                  Supported formats: PDF, DOCX (Max 10MB)
                </CardDescription>
              </div>
              {hasResume && (
                <Button
                  variant="outline"
                  size="sm"
                  className="text-error hover:bg-error/10 hover:text-error border-error/30"
                  onClick={() => setShowDeleteConfirm(true)}
                >
                  Delete Resume
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
                isDragging
                  ? 'border-brand-500 bg-brand-50'
                  : 'border-warm-200 hover:border-brand-300 hover:bg-warm-50'
              }`}
            >
              <div className="w-16 h-16 mx-auto mb-4 bg-brand-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <p className="text-warm-700 mb-2">
                {hasResume ? 'Upload a new resume to replace the current one' : 'Drag and drop your resume here, or'}
              </p>
              <label className="cursor-pointer">
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileSelect}
                  className="hidden"
                  disabled={isUploading}
                />
                <Button variant="brand" disabled={isUploading} asChild>
                  <span>{isUploading ? 'Processing...' : hasResume ? 'Choose New File' : 'Browse Files'}</span>
                </Button>
              </label>
              {isUploading && (
                <div className="mt-4 flex items-center justify-center gap-3 text-brand-600">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-brand-600"></div>
                  <span className="text-sm">Uploading and parsing with AI... This may take 20-30 seconds.</span>
                </div>
              )}
            </div>

            {uploadError && (
              <div className="mt-4 p-4 bg-error-light border border-error/20 rounded-xl">
                <p className="text-sm text-error-dark">{uploadError}</p>
              </div>
            )}

            {uploadSuccess && (
              <div className="mt-4 p-4 bg-success-light border border-success/20 rounded-xl">
                <p className="text-sm text-success-dark">Resume uploaded and parsed successfully!</p>
              </div>
            )}

            {/* Continue to Interview Button (onboarding mode) */}
            {isOnboarding && hasResume && (
              <div className="mt-6 p-6 bg-brand-50 border border-brand-100 rounded-xl">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-brand-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-warm-900 mb-1">Resume Ready!</h3>
                    <p className="text-warm-600 text-sm mb-4">
                      Your interview questions will be personalized based on your experience at{' '}
                      <span className="font-medium">{resumeData?.parsedData?.experience?.[0]?.company || 'your previous roles'}</span>.
                    </p>
                    <Button
                      variant="brand"
                      onClick={startInterview}
                      disabled={isStartingInterview}
                      className="w-full sm:w-auto"
                    >
                      {isStartingInterview ? 'Starting Interview...' : 'Continue to Interview'}
                      <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Parsed Resume Display */}
        {resumeData?.parsedData && (
          <ParsedResumeDisplay data={resumeData.parsedData} uploadedAt={resumeData.uploadedAt} />
        )}

        {!resumeData?.parsedData && !isLoading && (
          <Card className="bg-warm-50 border-warm-100">
            <CardContent className="py-12 text-center">
              <div className="w-16 h-16 bg-warm-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-warm-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-warm-900 mb-2">No resume uploaded yet</h3>
              <p className="text-warm-500">
                Upload your resume to get personalized interview questions and better job matches
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}

function ParsedResumeDisplay({ data, uploadedAt }: { data: ParsedResumeData; uploadedAt?: string }) {
  return (
    <div className="space-y-6">
      {/* Basic Info */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle>{data.name || 'Resume'}</CardTitle>
              {uploadedAt && (
                <CardDescription>
                  Uploaded on {new Date(uploadedAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </CardDescription>
              )}
            </div>
            <Badge variant="outline" className="bg-success-light text-success border-success/30">
              AI Parsed
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-2 gap-4">
            {data.email && (
              <div>
                <p className="text-sm text-warm-500">Email</p>
                <p className="text-warm-900">{data.email}</p>
              </div>
            )}
            {data.phone && (
              <div>
                <p className="text-sm text-warm-500">Phone</p>
                <p className="text-warm-900">{data.phone}</p>
              </div>
            )}
            {data.location && (
              <div>
                <p className="text-sm text-warm-500">Location</p>
                <p className="text-warm-900">{data.location}</p>
              </div>
            )}
          </div>
          {data.summary && (
            <div className="mt-4 pt-4 border-t border-warm-100">
              <p className="text-sm text-warm-500 mb-2">Summary</p>
              <p className="text-warm-700">{data.summary}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Skills */}
      {data.skills && data.skills.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Skills</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {data.skills.map((skill, index) => (
                <Badge key={index} variant="default">
                  {skill}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Experience */}
      {data.experience && data.experience.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Work Experience</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {data.experience.map((exp, index) => (
                <div key={index} className={index > 0 ? 'pt-6 border-t border-warm-100' : ''}>
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-medium text-warm-900">{exp.title}</h4>
                      <p className="text-brand-600">{exp.company}</p>
                    </div>
                    {(exp.startDate || exp.endDate) && (
                      <span className="text-sm text-warm-500">
                        {exp.startDate} - {exp.endDate || 'Present'}
                      </span>
                    )}
                  </div>
                  {exp.description && (
                    <p className="text-warm-600 text-sm mt-2">{exp.description}</p>
                  )}
                  {exp.highlights && exp.highlights.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {exp.highlights.map((highlight, hIndex) => (
                        <li key={hIndex} className="text-sm text-warm-600 flex items-start gap-2">
                          <span className="text-brand-500 mt-1">•</span>
                          {highlight}
                        </li>
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
      {data.education && data.education.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Education</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.education.map((edu, index) => (
                <div key={index} className={index > 0 ? 'pt-4 border-t border-warm-100' : ''}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-medium text-warm-900">{edu.institution}</h4>
                      {(edu.degree || edu.fieldOfStudy) && (
                        <p className="text-warm-600">
                          {edu.degree}{edu.degree && edu.fieldOfStudy && ' in '}{edu.fieldOfStudy}
                        </p>
                      )}
                    </div>
                    {(edu.startDate || edu.endDate) && (
                      <span className="text-sm text-warm-500">
                        {edu.startDate} - {edu.endDate || 'Present'}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Projects */}
      {data.projects && data.projects.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.projects.map((project, index) => (
                <div key={index} className={index > 0 ? 'pt-4 border-t border-warm-100' : ''}>
                  <h4 className="font-medium text-warm-900">{project.name}</h4>
                  {project.description && (
                    <p className="text-warm-600 text-sm mt-1">{project.description}</p>
                  )}
                  {project.technologies && project.technologies.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {project.technologies.map((tech, tIndex) => (
                        <Badge key={tIndex} variant="outline" className="text-xs">
                          {tech}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Languages & Certifications */}
      {((data.languages && data.languages.length > 0) || (data.certifications && data.certifications.length > 0)) && (
        <div className="grid sm:grid-cols-2 gap-6">
          {data.languages && data.languages.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Languages</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {data.languages.map((lang, index) => (
                    <Badge key={index} variant="outline">
                      {lang}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {data.certifications && data.certifications.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Certifications</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {data.certifications.map((cert, index) => (
                    <li key={index} className="text-warm-700 flex items-start gap-2">
                      <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {cert}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

// Wrapper with Suspense for useSearchParams
export default function ResumePage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-gradient-to-b from-brand-50 to-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600"></div>
      </main>
    }>
      <ResumePageContent />
    </Suspense>
  )
}
