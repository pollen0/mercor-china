'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { vibeCodeApi, VibeCodeSession, VibeCodeSessionList } from '@/lib/api'

// ============================================================================
// Constants
// ============================================================================

const SOURCE_LABELS: Record<string, string> = {
  cursor: 'Cursor',
  claude_code: 'Claude Code',
  copilot: 'GitHub Copilot',
  chatgpt: 'ChatGPT',
  other: 'Other',
}

const ARCHETYPE_LABELS: Record<string, { label: string; color: string; description: string }> = {
  architect: {
    label: 'Architect',
    color: 'bg-stone-900 text-white',
    description: 'Plans thoroughly, designs before building, questions AI decisions',
  },
  iterative_builder: {
    label: 'Iterative Builder',
    color: 'bg-teal-50 text-teal-700',
    description: 'Builds incrementally, tests often, refines through cycles',
  },
  experimenter: {
    label: 'Experimenter',
    color: 'bg-stone-100 text-stone-700',
    description: 'Curious and exploratory, tries multiple approaches before committing',
  },
  ai_dependent: {
    label: 'AI Dependent',
    color: 'bg-amber-50 text-amber-700',
    description: 'Relies heavily on AI for decisions - consider leading more',
  },
  copy_paster: {
    label: 'Copy Paster',
    color: 'bg-red-50 text-red-700',
    description: 'Minimal steering of the AI - try being more intentional',
  },
}

const EXPORT_GUIDES: Record<string, { tool: string; steps: string[] }> = {
  cursor: {
    tool: 'Cursor',
    steps: [
      'Open the Composer or Chat panel with your session',
      'Select all the conversation text (Cmd/Ctrl+A) and copy it',
      'Or find your session logs in ~/Library/Application Support/Cursor/User/workspaceStorage/',
      'Paste the conversation or upload the .json log file here',
    ],
  },
  claude_code: {
    tool: 'Claude Code',
    steps: [
      'Your session transcripts are saved in ~/.claude/projects/',
      'Find the .jsonl file for your session in the project folder',
      'Or select the full conversation in your terminal and copy it',
      'Upload the .jsonl file or paste the conversation here',
    ],
  },
  copilot: {
    tool: 'GitHub Copilot Chat',
    steps: [
      'Open VS Code with the Copilot Chat panel visible',
      'Select the full conversation (Cmd/Ctrl+A) and copy it',
      'You can also find logs via VS Code: Help > Toggle Developer Tools > Console',
      'Paste the conversation text here',
    ],
  },
  chatgpt: {
    tool: 'ChatGPT',
    steps: [
      'Open your coding conversation on chat.openai.com',
      'Click the share icon at the top of the conversation',
      'Select "Copy Link" or select all text and copy',
      'Paste the conversation content here',
    ],
  },
}

// ============================================================================
// Session Card Component (student view - qualitative only, NO scores)
// ============================================================================

function SessionCard({
  session,
  onDelete,
  onReanalyze,
}: {
  session: VibeCodeSession
  onDelete: (id: string) => void
  onReanalyze: (id: string) => void
}) {
  const isAnalyzing = session.analysisStatus === 'analyzing' || session.analysisStatus === 'pending'
  const isFailed = session.analysisStatus === 'failed'
  const isCompleted = session.analysisStatus === 'completed'

  return (
    <div className="border border-stone-200 rounded-lg p-4 space-y-3">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h4 className="font-medium text-stone-900">
            {session.title || 'Untitled Session'}
          </h4>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs px-2 py-0.5 rounded-full bg-stone-100 text-stone-600">
              {SOURCE_LABELS[session.source] || session.source}
            </span>
            {session.messageCount && (
              <span className="text-xs text-stone-400">
                {session.messageCount} exchanges
              </span>
            )}
            {session.uploadedAt && (
              <span className="text-xs text-stone-400">
                {new Date(session.uploadedAt).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isFailed && (
            <button
              onClick={() => onReanalyze(session.id)}
              className="text-xs text-stone-600 hover:text-stone-900"
            >
              Retry
            </button>
          )}
          <button
            onClick={() => onDelete(session.id)}
            className="text-xs text-stone-400 hover:text-red-500"
          >
            Remove
          </button>
        </div>
      </div>

      {/* Status: Analyzing */}
      {isAnalyzing && (
        <div className="flex items-center gap-2 text-sm text-stone-500">
          <div className="animate-spin h-4 w-4 border-2 border-stone-200 border-t-stone-600 rounded-full" />
          Analyzing your session with Claude...
        </div>
      )}

      {/* Status: Failed */}
      {isFailed && (
        <div className="text-sm text-red-500 bg-red-50 rounded p-2">
          Analysis failed. Click &ldquo;Retry&rdquo; to try again.
        </div>
      )}

      {/* Completed: show confirmation only (feedback is employer-only) */}
      {isCompleted && (
        <div className="flex items-center gap-2 text-sm text-teal-700">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Analysis complete. Your builder profile is visible to employers.
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Upload Form Component
// ============================================================================

function UploadForm({
  onUpload,
  isUploading,
}: {
  onUpload: (data: { sessionContent: string; title?: string; source?: string; description?: string; projectUrl?: string }) => void
  isUploading: boolean
}) {
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [source, setSource] = useState('')
  const [projectUrl, setProjectUrl] = useState('')
  const [showGuide, setShowGuide] = useState<string | null>(null)
  const [showCli, setShowCli] = useState(false)
  const [showPasteArea, setShowPasteArea] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [sourceDropdownOpen, setSourceDropdownOpen] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileRead = useCallback((file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      setContent(text)
      if (!title) {
        const name = file.name.replace(/\.(json|md|txt|log)$/i, '')
        setTitle(name)
      }
    }
    reader.readAsText(file)
  }, [title])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileRead(file)
  }, [handleFileRead])

  const handleSubmit = () => {
    if (!content.trim()) return
    onUpload({
      sessionContent: content,
      title: title || undefined,
      description: description || undefined,
      source: source || undefined,
      projectUrl: projectUrl || undefined,
    })
    setContent('')
    setTitle('')
    setDescription('')
    setSource('')
    setProjectUrl('')
  }

  return (
    <div className="space-y-4">
      {/* Export Guides + CLI */}
      <div className="flex flex-wrap gap-2">
        <span className="text-sm text-stone-500">How to export:</span>
        {Object.entries(EXPORT_GUIDES).map(([key, guide]) => (
          <button
            key={key}
            onClick={() => { setShowGuide(showGuide === key ? null : key); setShowCli(false) }}
            className={`text-xs px-2 py-1 rounded border transition-colors ${
              showGuide === key
                ? 'border-stone-900 bg-stone-50 text-stone-900'
                : 'border-stone-200 text-stone-600 hover:border-stone-300'
            }`}
          >
            {guide.tool}
          </button>
        ))}
        <button
          onClick={() => { setShowCli(!showCli); setShowGuide(null) }}
          className={`text-xs px-2 py-1 rounded border transition-colors ${
            showCli
              ? 'border-stone-900 bg-stone-50 text-stone-900'
              : 'border-stone-200 text-stone-600 hover:border-stone-300'
          }`}
        >
          CLI / Terminal
        </button>
      </div>

      {/* Guide Steps */}
      {showGuide && EXPORT_GUIDES[showGuide] && (
        <div className="bg-stone-50 rounded-lg p-3 text-sm">
          <h5 className="font-medium text-stone-700 mb-2">
            Export from {EXPORT_GUIDES[showGuide].tool}:
          </h5>
          <ol className="space-y-1 text-stone-600">
            {EXPORT_GUIDES[showGuide].steps.map((step, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-stone-400 font-mono text-xs mt-0.5">{i + 1}.</span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* CLI Instructions */}
      {showCli && (
        <div className="bg-stone-900 rounded-lg p-4 text-sm font-mono">
          <p className="text-stone-400 text-xs mb-2"># Upload from your terminal:</p>
          <p className="text-stone-400 text-xs mb-3">
            # Get your auth token from browser DevTools: localStorage.getItem(&apos;candidate_token&apos;)
          </p>
          <div className="space-y-3">
            <div>
              <p className="text-stone-500 text-xs mb-1"># Upload a Claude Code session transcript</p>
              <p className="text-white text-xs break-all">
                cat ~/.claude/projects/YOUR_PROJECT/*.jsonl | \<br />
                &nbsp;&nbsp;jq -Rs &apos;{'{'}session_content: .{'}'}&apos; | \<br />
                &nbsp;&nbsp;curl -X POST -H &quot;Authorization: Bearer $TOKEN&quot; \<br />
                &nbsp;&nbsp;-H &quot;Content-Type: application/json&quot; -d @- \<br />
                &nbsp;&nbsp;https://pathway.careers/api/vibe-code/sessions/raw
              </p>
            </div>
            <div>
              <p className="text-stone-500 text-xs mb-1"># Upload any conversation file (.json, .txt, .md)</p>
              <p className="text-white text-xs break-all">
                jq -Rs &apos;{'{'}session_content: .{'}'}&apos; my-session.json | \<br />
                &nbsp;&nbsp;curl -X POST -H &quot;Authorization: Bearer $TOKEN&quot; \<br />
                &nbsp;&nbsp;-H &quot;Content-Type: application/json&quot; -d @- \<br />
                &nbsp;&nbsp;https://pathway.careers/api/vibe-code/sessions/raw
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Drop Zone / File Upload / Paste Area */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-lg transition-colors ${
          dragOver
            ? 'border-stone-400 bg-stone-50'
            : content
              ? 'border-teal-300 bg-teal-50'
              : 'border-stone-200 hover:border-stone-300'
        }`}
      >
        {!content ? (
          <div className="p-6 text-center">
            <div className="text-stone-400 mb-2">
              <svg className="mx-auto h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p className="text-sm text-stone-600 mb-1">
              Drag & drop your conversation file, or{' '}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-stone-900 hover:text-stone-700 font-medium underline"
              >
                browse files
              </button>
            </p>
            <p className="text-xs text-stone-400 mb-3">
              Upload .json, .jsonl, .md, or .txt — your AI chat logs from any coding project
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json,.jsonl,.md,.txt,.log"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleFileRead(file)
              }}
            />

            {/* Paste options */}
            <div className="flex items-center gap-2 justify-center mb-2">
              <div className="h-px bg-stone-200 w-12" />
              <span className="text-xs text-stone-400">or paste your session</span>
              <div className="h-px bg-stone-200 w-12" />
            </div>
            <div className="flex items-center gap-2 justify-center">
              <button
                onClick={async () => {
                  try {
                    const text = await navigator.clipboard.readText()
                    if (text) setContent(text)
                  } catch {
                    setShowPasteArea(true)
                  }
                }}
                className="text-xs text-stone-900 hover:text-stone-700 font-medium"
              >
                Paste from clipboard
              </button>
              <span className="text-xs text-stone-300">|</span>
              <button
                onClick={() => setShowPasteArea(!showPasteArea)}
                className="text-xs text-stone-500 hover:text-stone-700"
              >
                Type/paste manually
              </button>
            </div>

            {/* Manual paste textarea */}
            {showPasteArea && (
              <div className="mt-3 text-left">
                <textarea
                  className="w-full h-32 text-xs font-mono border border-stone-200 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-stone-900/10 resize-y"
                  placeholder="Paste your AI coding session content here..."
                  onChange={(e) => {
                    if (e.target.value.length > 50) {
                      setContent(e.target.value)
                      setShowPasteArea(false)
                    }
                  }}
                />
                <p className="text-xs text-stone-400 mt-1">Start typing or paste - will auto-load when content is detected</p>
              </div>
            )}
          </div>
        ) : (
          <div className="p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-teal-700 font-medium">
                Session loaded ({content.length.toLocaleString()} characters)
              </span>
              <button
                onClick={() => setContent('')}
                className="text-xs text-stone-400 hover:text-stone-600"
              >
                Clear
              </button>
            </div>
            <pre className="text-xs text-stone-500 bg-white rounded p-2 max-h-24 overflow-y-auto border border-stone-100">
              {content.slice(0, 500)}{content.length > 500 ? '...' : ''}
            </pre>
          </div>
        )}
      </div>

      {/* Metadata Fields */}
      {content && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-stone-500 block mb-1">Title (optional)</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Built a REST API"
              className="w-full text-sm border border-stone-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
            />
          </div>
          <div className="relative">
            <label className="text-xs text-stone-500 block mb-1">Tool (auto-detected)</label>
            <button
              type="button"
              onClick={() => setSourceDropdownOpen(!sourceDropdownOpen)}
              className="w-full flex items-center justify-between px-3 py-1.5 border border-stone-200 rounded-lg text-sm text-left hover:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
            >
              <span className="text-stone-900">
                {source ? (SOURCE_LABELS[source] || source) : 'Auto-detect'}
              </span>
              <svg className="w-4 h-4 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {sourceDropdownOpen && (
              <div className="absolute z-10 mt-1 w-full bg-white border border-stone-200 rounded-lg shadow-lg py-1 max-h-60 overflow-auto">
                {[
                  { value: '', label: 'Auto-detect' },
                  { value: 'cursor', label: 'Cursor' },
                  { value: 'claude_code', label: 'Claude Code' },
                  { value: 'copilot', label: 'GitHub Copilot' },
                  { value: 'chatgpt', label: 'ChatGPT' },
                  { value: 'other', label: 'Other' },
                ].map(option => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => { setSource(option.value); setSourceDropdownOpen(false) }}
                    className={`w-full px-3 py-2 text-left text-sm transition-colors ${
                      source === option.value
                        ? 'bg-stone-50 text-stone-900 font-medium'
                        : 'text-stone-700 hover:bg-stone-50'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="sm:col-span-2">
            <label className="text-xs text-stone-500 block mb-1">What did you build? (optional)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Full-stack todo app with auth and real-time updates"
              className="w-full text-sm border border-stone-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="text-xs text-stone-500 block mb-1">Project URL (optional)</label>
            <input
              type="url"
              value={projectUrl}
              onChange={(e) => setProjectUrl(e.target.value)}
              placeholder="https://github.com/you/project"
              className="w-full text-sm border border-stone-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-stone-900/10"
            />
          </div>
        </div>
      )}

      {/* Submit */}
      {content && (
        <button
          onClick={handleSubmit}
          disabled={isUploading || !content.trim()}
          className="w-full py-2 bg-stone-900 text-white rounded-lg text-sm font-medium hover:bg-stone-800 disabled:opacity-50 transition-colors"
        >
          {isUploading ? 'Uploading...' : 'Upload & Analyze Session'}
        </button>
      )}
    </div>
  )
}

// ============================================================================
// Main Section Component
// ============================================================================

interface VibeCodeSectionProps {
  initialData?: VibeCodeSessionList | null
  onDataChange?: () => void
}

export default function VibeCodeSection({ initialData, onDataChange }: VibeCodeSectionProps) {
  const [sessions, setSessions] = useState<VibeCodeSession[]>(initialData?.sessions || [])
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showUpload, setShowUpload] = useState(false)
  const [isLoading, setIsLoading] = useState(!initialData)

  // Fetch sessions on mount if no initialData provided
  useEffect(() => {
    if (!initialData) {
      const loadSessions = async () => {
        try {
          const data = await vibeCodeApi.listSessions()
          setSessions(data.sessions)
        } catch (err) {
          console.error('Failed to load vibe code sessions:', err)
        } finally {
          setIsLoading(false)
        }
      }
      loadSessions()
    }
  }, [initialData])

  const handleUpload = useCallback(async (data: Parameters<typeof vibeCodeApi.upload>[0]) => {
    setIsUploading(true)
    setError(null)
    try {
      const result = await vibeCodeApi.upload(data)
      setSessions(prev => [result.session, ...prev])
      setShowUpload(false)

      // Poll for analysis completion
      const pollInterval = setInterval(async () => {
        try {
          const updated = await vibeCodeApi.listSessions()
          setSessions(updated.sessions)
          const session = updated.sessions.find(s => s.id === result.session.id)
          if (session && (session.analysisStatus === 'completed' || session.analysisStatus === 'failed')) {
            clearInterval(pollInterval)
            onDataChange?.()
          }
        } catch {
          clearInterval(pollInterval)
        }
      }, 5000)

      setTimeout(() => clearInterval(pollInterval), 180000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setIsUploading(false)
    }
  }, [onDataChange])

  const handleDelete = useCallback(async (sessionId: string) => {
    try {
      await vibeCodeApi.deleteSession(sessionId)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
    } catch {
      setError('Failed to delete session')
    }
  }, [])

  const handleReanalyze = useCallback(async (sessionId: string) => {
    try {
      const updated = await vibeCodeApi.reanalyze(sessionId)
      setSessions(prev => prev.map(s => s.id === sessionId ? updated : s))
      const pollInterval = setInterval(async () => {
        try {
          const data = await vibeCodeApi.listSessions()
          setSessions(data.sessions)
          const session = data.sessions.find(s => s.id === sessionId)
          if (session && (session.analysisStatus === 'completed' || session.analysisStatus === 'failed')) {
            clearInterval(pollInterval)
          }
        } catch {
          clearInterval(pollInterval)
        }
      }, 5000)
      setTimeout(() => clearInterval(pollInterval), 180000)
    } catch {
      setError('Failed to reanalyze session')
    }
  }, [])

  const completedSessions = sessions.filter(s => s.analysisStatus === 'completed')

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="flex items-center gap-2">
              AI Builder Profile
              {completedSessions.length > 0 && (
                <span className="text-xs font-normal px-2 py-0.5 rounded-full bg-teal-50 text-teal-700">
                  {completedSessions.length} session{completedSessions.length !== 1 ? 's' : ''} analyzed
                </span>
              )}
            </CardTitle>
            <CardDescription>
              Upload your AI coding conversations from building real projects. We analyze how you direct the AI, make decisions, and iterate — not the code itself.
            </CardDescription>
          </div>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="text-sm px-3 py-1.5 rounded-lg border border-stone-200 text-stone-600 hover:bg-stone-50 transition-colors"
          >
            {showUpload ? 'Cancel' : '+ Upload Session'}
          </button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Loading */}
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin h-5 w-5 border-2 border-stone-200 border-t-stone-600 rounded-full" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="text-sm text-red-600 bg-red-50 rounded-lg p-3">
            {error}
            <button onClick={() => setError(null)} className="ml-2 underline text-xs">
              Dismiss
            </button>
          </div>
        )}

        {/* Upload Form */}
        {showUpload && (
          <UploadForm onUpload={handleUpload} isUploading={isUploading} />
        )}

        {/* Empty State */}
        {!isLoading && sessions.length === 0 && !showUpload && (
          <div className="text-center py-8">
            <div className="text-stone-300 mb-3">
              <svg className="mx-auto h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <h4 className="text-sm font-medium text-stone-700 mb-1">Show employers how you build</h4>
            <p className="text-xs text-stone-500 mb-2 max-w-sm mx-auto">
              Already built a project with AI tools? Upload the conversation log from Cursor, Claude Code, Copilot, or ChatGPT.
            </p>
            <p className="text-xs text-stone-400 mb-4 max-w-sm mx-auto">
              We analyze your AI conversations — how you direct the AI, handle errors, and make design decisions. Upload as many sessions as you want from different projects.
            </p>
            <button
              onClick={() => setShowUpload(true)}
              className="text-sm px-4 py-2 bg-stone-900 text-white rounded-lg hover:bg-stone-800 transition-colors"
            >
              Upload Your First Session
            </button>
          </div>
        )}

        {/* Session List */}
        {sessions.length > 0 && (
          <div className="space-y-3">
            {sessions.map(session => (
              <SessionCard
                key={session.id}
                session={session}
                onDelete={handleDelete}
                onReanalyze={handleReanalyze}
              />
            ))}
          </div>
        )}

        {/* Summary for multiple sessions */}
        {completedSessions.length >= 2 && (
          <div className="bg-stone-50 rounded-lg p-3 text-center">
            <p className="text-xs text-stone-500">
              {completedSessions.length} sessions analyzed. Upload more sessions to build a stronger builder profile for employers.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
