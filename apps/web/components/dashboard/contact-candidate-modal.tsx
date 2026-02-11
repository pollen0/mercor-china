'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface ContactCandidateModalProps {
  isOpen: boolean
  onClose: () => void
  candidateId: string
  candidateName: string
  candidateEmail: string
  jobId?: string
  jobTitle?: string
  onSend: (data: { subject: string; body: string; messageType: string; jobId?: string }) => Promise<void>
}

const MESSAGE_TEMPLATES = [
  {
    type: 'interview_request',
    label: 'Interview Request',
    subject: 'Interview Invitation - {jobTitle}',
    body: `Dear {candidateName},

We were impressed by your interview performance and would like to invite you for the next round of interviews for the {jobTitle} position.

Please let us know your availability for the coming week.

Best regards,
{companyName}`
  },
  {
    type: 'shortlist_notice',
    label: 'Shortlist Notice',
    subject: 'Good News! You have been shortlisted',
    body: `Dear {candidateName},

Congratulations! We are pleased to inform you that you have been shortlisted for the {jobTitle} position.

We will be in touch soon with next steps.

Best regards,
{companyName}`
  },
  {
    type: 'rejection',
    label: 'Rejection',
    subject: 'Application Update - {jobTitle}',
    body: `Dear {candidateName},

Thank you for taking the time to interview for the {jobTitle} position.

After careful consideration, we have decided to move forward with other candidates whose experience more closely matches our current needs.

We appreciate your interest in our company and wish you the best in your job search.

Best regards,
{companyName}`
  },
  {
    type: 'custom',
    label: 'Custom Message',
    subject: '',
    body: ''
  }
]

export function ContactCandidateModal({
  isOpen,
  onClose,
  candidateId,
  candidateName,
  candidateEmail,
  jobId,
  jobTitle,
  onSend
}: ContactCandidateModalProps) {
  const [selectedTemplate, setSelectedTemplate] = useState('custom')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const applyTemplate = (templateType: string) => {
    setSelectedTemplate(templateType)
    const template = MESSAGE_TEMPLATES.find(t => t.type === templateType)
    if (template) {
      // Replace placeholders
      const processedSubject = template.subject
        .replace('{jobTitle}', jobTitle || 'the position')
        .replace('{candidateName}', candidateName)
      const processedBody = template.body
        .replace(/{candidateName}/g, candidateName)
        .replace(/{jobTitle}/g, jobTitle || 'the position')
        .replace(/{companyName}/g, 'Our Team')

      setSubject(processedSubject)
      setBody(processedBody)
    }
    setError(null)
  }

  const handleSend = async () => {
    if (!subject.trim()) {
      setError('Please enter a subject')
      return
    }
    if (!body.trim()) {
      setError('Please enter a message')
      return
    }

    setIsSending(true)
    setError(null)

    try {
      await onSend({
        subject,
        body,
        messageType: selectedTemplate,
        jobId
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setIsSending(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="border-b p-4 flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-lg">Contact Candidate</h2>
            <p className="text-sm text-stone-500">
              Send a message to {candidateName} ({candidateEmail})
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-stone-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-stone-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Template Selection */}
          <div>
            <Label className="text-sm font-medium">Message Template</Label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
              {MESSAGE_TEMPLATES.map(template => (
                <button
                  key={template.type}
                  onClick={() => applyTemplate(template.type)}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                    selectedTemplate === template.type
                      ? 'border-teal-500 bg-teal-50 text-teal-700'
                      : 'border-stone-200 hover:border-stone-300'
                  }`}
                >
                  {template.label}
                </button>
              ))}
            </div>
          </div>

          {/* Subject */}
          <div className="space-y-2">
            <Label htmlFor="subject">Subject</Label>
            <Input
              id="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Enter subject..."
            />
          </div>

          {/* Body */}
          <div className="space-y-2">
            <Label htmlFor="body">Message</Label>
            <textarea
              id="body"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Enter your message..."
              rows={10}
              className="w-full px-3 py-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>

          {/* Error */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t p-4 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose} disabled={isSending}>
            Cancel
          </Button>
          <Button
            onClick={handleSend}
            disabled={isSending}
            className="bg-teal-600 hover:bg-teal-700"
          >
            {isSending ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Sending...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Send Message
              </span>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
