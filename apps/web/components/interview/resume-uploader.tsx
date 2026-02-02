'use client'

import { useState, useRef, useCallback } from 'react'
import { Button } from '@/components/ui/button'

interface ParsedResume {
  name?: string
  email?: string
  phone?: string
  location?: string
  summary?: string
  skills: string[]
  experience: Array<{
    company: string
    title: string
    startDate?: string
    endDate?: string
    description?: string
  }>
  education: Array<{
    institution: string
    degree?: string
    fieldOfStudy?: string
  }>
}

interface ResumeParseResult {
  success: boolean
  message: string
  resumeUrl?: string
  parsedData?: ParsedResume
  rawTextPreview?: string
}

interface ResumeUploaderProps {
  candidateId: string
  onUploadComplete?: (result: ResumeParseResult) => void
  onSkip?: () => void
}

export function ResumeUploader({ candidateId, onUploadComplete, onSkip }: ResumeUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ResumeParseResult | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

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

    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFile(files[0])
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFile(files[0])
    }
  }, [])

  const handleFile = async (file: File) => {
    // Validate file type
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    const validExtensions = ['.pdf', '.docx']

    const hasValidType = validTypes.includes(file.type)
    const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))

    if (!hasValidType && !hasValidExtension) {
      setError('Please upload a PDF or Word document (.pdf or .docx)')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setError(null)
    setIsUploading(true)
    setUploadProgress('Uploading resume...')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/candidates/${candidateId}/resume`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      setUploadProgress('Parsing resume...')

      const data = await response.json()

      // Convert snake_case to camelCase
      const parsedResult: ResumeParseResult = {
        success: data.success,
        message: data.message,
        resumeUrl: data.resume_url,
        rawTextPreview: data.raw_text_preview,
        parsedData: data.parsed_data ? {
          name: data.parsed_data.name,
          email: data.parsed_data.email,
          phone: data.parsed_data.phone,
          location: data.parsed_data.location,
          summary: data.parsed_data.summary,
          skills: data.parsed_data.skills || [],
          experience: (data.parsed_data.experience || []).map((exp: Record<string, unknown>) => ({
            company: exp.company,
            title: exp.title,
            startDate: exp.start_date,
            endDate: exp.end_date,
            description: exp.description,
          })),
          education: (data.parsed_data.education || []).map((edu: Record<string, unknown>) => ({
            institution: edu.institution,
            degree: edu.degree,
            fieldOfStudy: edu.field_of_study,
          })),
        } : undefined
      }

      setResult(parsedResult)
      onUploadComplete?.(parsedResult)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload resume')
    } finally {
      setIsUploading(false)
      setUploadProgress('')
    }
  }

  const handleBrowseClick = () => {
    fileInputRef.current?.click()
  }

  const handleRetry = () => {
    setResult(null)
    setError(null)
  }

  // Show result view if upload was successful
  if (result && result.success) {
    return (
      <div className="space-y-6">
        <div className="bg-green-50 border border-green-200 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-green-800">Resume Uploaded Successfully</h3>
              <p className="text-sm text-green-600 mt-1">{result.message}</p>
            </div>
          </div>
        </div>

        {/* Parsed Data Preview */}
        {result.parsedData && (
          <div className="bg-white border rounded-xl p-6 space-y-4">
            <h4 className="font-medium text-gray-900">Extracted Information</h4>

            {/* Skills */}
            {result.parsedData.skills.length > 0 && (
              <div>
                <p className="text-sm text-gray-500 mb-2">Skills</p>
                <div className="flex flex-wrap gap-2">
                  {result.parsedData.skills.slice(0, 10).map((skill, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 bg-teal-50 text-teal-700 rounded-full text-sm border border-teal-200"
                    >
                      {skill}
                    </span>
                  ))}
                  {result.parsedData.skills.length > 10 && (
                    <span className="px-3 py-1 text-gray-500 text-sm">
                      +{result.parsedData.skills.length - 10} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Experience */}
            {result.parsedData.experience.length > 0 && (
              <div>
                <p className="text-sm text-gray-500 mb-2">Recent Experience</p>
                <div className="space-y-2">
                  {result.parsedData.experience.slice(0, 2).map((exp, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg p-3">
                      <p className="font-medium text-gray-900">{exp.title}</p>
                      <p className="text-sm text-gray-600">{exp.company}</p>
                      {exp.startDate && (
                        <p className="text-xs text-gray-500 mt-1">
                          {exp.startDate} - {exp.endDate || 'Present'}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {result.parsedData.education.length > 0 && (
              <div>
                <p className="text-sm text-gray-500 mb-2">Education</p>
                <div className="space-y-2">
                  {result.parsedData.education.slice(0, 2).map((edu, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg p-3">
                      <p className="font-medium text-gray-900">{edu.institution}</p>
                      {edu.degree && (
                        <p className="text-sm text-gray-600">
                          {edu.degree}{edu.fieldOfStudy ? ` in ${edu.fieldOfStudy}` : ''}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleRetry}
            className="flex-1"
          >
            Upload Different Resume
          </Button>
          {onSkip && (
            <Button
              onClick={onSkip}
              className="flex-1 bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-700 hover:to-teal-600"
            >
              Continue
            </Button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer
          ${isDragging
            ? 'border-teal-500 bg-teal-50'
            : 'border-gray-300 hover:border-teal-400 hover:bg-gray-50'
          }
          ${isUploading ? 'pointer-events-none opacity-60' : ''}
        `}
        onClick={handleBrowseClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileSelect}
          className="hidden"
        />

        {isUploading ? (
          <div className="space-y-3">
            <div className="w-12 h-12 border-2 border-gray-200 border-t-teal-600 rounded-full animate-spin mx-auto" />
            <p className="text-gray-600">{uploadProgress}</p>
          </div>
        ) : (
          <>
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p className="text-gray-700 font-medium mb-1">
              Drag & drop your resume here
            </p>
            <p className="text-gray-500 text-sm mb-3">
              or click to browse
            </p>
            <p className="text-gray-400 text-xs">
              Supports PDF and Word documents (max 10MB)
            </p>
          </>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="text-red-700 text-sm">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-red-600 text-sm underline mt-1 hover:no-underline"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Skip Button */}
      {onSkip && (
        <Button
          variant="ghost"
          onClick={onSkip}
          className="w-full text-gray-500 hover:text-gray-700"
        >
          Skip for now
        </Button>
      )}
    </div>
  )
}
