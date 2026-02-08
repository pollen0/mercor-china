'use client'

import { useState, useCallback, useRef } from 'react'
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
    color: 'bg-indigo-100 text-indigo-800',
    description: 'Plans thoroughly, designs before building, questions AI decisions',
  },
  iterative_builder: {
    label: 'Iterative Builder',
    color: 'bg-emerald-100 text-emerald-800',
    description: 'Builds incrementally, tests often, refines through cycles',
  },
  experimenter: {
    label: 'Experimenter',
    color: 'bg-amber-100 text-amber-800',
    description: 'Curious and exploratory, tries multiple approaches before committing',
  },
  ai_dependent: {
    label: 'AI Dependent',
    color: 'bg-orange-100 text-orange-800',
    description: 'Relies heavily on AI for decisions - consider leading more',
  },
  copy_paster: {
    label: 'Copy Paster',
    color: 'bg-red-100 text-red-800',
    description: 'Minimal steering of the AI - try being more intentional',
  },
}

const EXPORT_GUIDES: Record<string, { tool: string; steps: string[] }> = {
  cursor: {
    tool: 'Cursor',
    steps: [
      'Open Cursor and go to the chat/composer panel',
      'Click the "..." menu at the top of the conversation',
      'Select "Export Chat" or "Copy Conversation"',
      'Paste or upload the exported content here',
    ],
  },
  claude_code: {
    tool: 'Claude Code',
    steps: [
      'In your terminal, run: claude export --format json',
      'Or copy the conversation from the Claude Code transcript',
      'You can also find session logs in ~/.claude/sessions/',
      'Upload the .json file or paste the content here',
    ],
  },
  copilot: {
    tool: 'GitHub Copilot Chat',
    steps: [
      'Open VS Code with Copilot Chat active',
      'Click the "..." menu in the chat panel',
      'Select "Export Chat Session"',
      'Upload the exported file here',
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
  const archetype = session.builderArchetype ? ARCHETYPE_LABELS[session.builderArchetype] : null
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
              className="text-xs text-indigo-600 hover:text-indigo-800"
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
          <div className="animate-spin h-4 w-4 border-2 border-indigo-500 border-t-transparent rounded-full" />
          Analyzing your session with Claude...
        </div>
      )}

      {/* Status: Failed */}
      {isFailed && (
        <div className="text-sm text-red-500 bg-red-50 rounded p-2">
          Analysis failed. Click &ldquo;Retry&rdquo; to try again.
        </div>
      )}

      {/* Completed: just show confirmation (all feedback is employer-only) */}
      {isCompleted && (
        <div className="flex items-center gap-2 text-sm text-emerald-600">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Analysis complete. Employers can view your builder profile.
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
                ? 'border-indigo-300 bg-indigo-50 text-indigo-700'
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
              ? 'border-indigo-300 bg-indigo-50 text-indigo-700'
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
          <p className="text-stone-400 text-xs mb-2"># Upload directly from your terminal:</p>
          <p className="text-emerald-400 text-xs mb-3">
            # Get your auth token from browser: localStorage.getItem(&apos;candidate_token&apos;)
          </p>
          <div className="space-y-3">
            <div>
              <p className="text-stone-500 text-xs mb-1"># Claude Code - pipe session directly</p>
              <p className="text-white text-xs break-all">
                claude export --format json | jq -Rs &apos;{'{'}session_content: .{'}'}&apos; | \<br />
                &nbsp;&nbsp;curl -X POST -H &quot;Authorization: Bearer $TOKEN&quot; \<br />
                &nbsp;&nbsp;-H &quot;Content-Type: application/json&quot; -d @- \<br />
                &nbsp;&nbsp;https://pathway.careers/api/vibe-code/sessions/raw
              </p>
            </div>
            <div>
              <p className="text-stone-500 text-xs mb-1"># Upload any session file</p>
              <p className="text-white text-xs break-all">
                jq -Rs &apos;{'{'}session_content: .{'}'}&apos; session.json | \<br />
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
            ? 'border-indigo-400 bg-indigo-50'
            : content
              ? 'border-emerald-300 bg-emerald-50'
              : 'border-stone-200 hover:border-stone-300'
        }`}
      >
        {!content ? (
          <div className="p-6 text-center">
            <div className="text-stone-400 mb-2">
              <svg className="mx-auto h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <p className="text-sm text-stone-600 mb-1">
              Drag & drop your session file, or{' '}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-indigo-600 hover:text-indigo-800 font-medium"
              >
                browse files
              </button>
            </p>
            <p className="text-xs text-stone-400 mb-3">
              Supports .json, .md, .txt exports from Cursor, Claude Code, Copilot
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json,.md,.txt,.log"
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
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
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
                  className="w-full h-32 text-xs font-mono border border-stone-200 rounded-lg p-3 focus:outline-none focus:ring-1 focus:ring-indigo-300 resize-y"
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
              <span className="text-sm text-emerald-700 font-medium">
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
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-stone-500 block mb-1">Title (optional)</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Built a REST API"
              className="w-full text-sm border border-stone-200 rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-300"
            />
          </div>
          <div>
            <label className="text-xs text-stone-500 block mb-1">Tool (auto-detected)</label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full text-sm border border-stone-200 rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-300"
            >
              <option value="">Auto-detect</option>
              <option value="cursor">Cursor</option>
              <option value="claude_code">Claude Code</option>
              <option value="copilot">GitHub Copilot</option>
              <option value="chatgpt">ChatGPT</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="col-span-2">
            <label className="text-xs text-stone-500 block mb-1">What did you build? (optional)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Full-stack todo app with auth and real-time updates"
              className="w-full text-sm border border-stone-200 rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-300"
            />
          </div>
          <div className="col-span-2">
            <label className="text-xs text-stone-500 block mb-1">Project URL (optional)</label>
            <input
              type="url"
              value={projectUrl}
              onChange={(e) => setProjectUrl(e.target.value)}
              placeholder="https://github.com/you/project"
              className="w-full text-sm border border-stone-200 rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-300"
            />
          </div>
        </div>
      )}

      {/* Submit */}
      {content && (
        <button
          onClick={handleSubmit}
          disabled={isUploading || !content.trim()}
          className="w-full py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg text-sm font-medium hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 transition-all"
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
                <span className="text-xs font-normal px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
                  {completedSessions.length} session{completedSessions.length !== 1 ? 's' : ''} analyzed
                </span>
              )}
            </CardTitle>
            <CardDescription>
              Upload your AI coding sessions to show employers how you think and build with tools like Cursor, Claude Code, and Copilot
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
        {sessions.length === 0 && !showUpload && (
          <div className="text-center py-8">
            <div className="text-stone-300 mb-3">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                  d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <h4 className="text-sm font-medium text-stone-700 mb-1">Show employers how you build</h4>
            <p className="text-xs text-stone-500 mb-4 max-w-sm mx-auto">
              Upload your AI coding sessions from Cursor, Claude Code, or Copilot.
              We&apos;ll analyze how you think and give you feedback on your building style.
            </p>
            <button
              onClick={() => setShowUpload(true)}
              className="text-sm px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all"
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
