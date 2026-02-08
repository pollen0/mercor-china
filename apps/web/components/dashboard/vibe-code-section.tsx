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
    description: 'Plans thoroughly, designs before building',
  },
  iterative_builder: {
    label: 'Iterative Builder',
    color: 'bg-emerald-100 text-emerald-800',
    description: 'Builds incrementally, refines through cycles',
  },
  experimenter: {
    label: 'Experimenter',
    color: 'bg-amber-100 text-amber-800',
    description: 'Explores alternatives, tries many approaches',
  },
  ai_dependent: {
    label: 'AI Dependent',
    color: 'bg-orange-100 text-orange-800',
    description: 'Relies heavily on AI for decisions',
  },
  copy_paster: {
    label: 'Copy Paster',
    color: 'bg-red-100 text-red-800',
    description: 'Minimal effort, pastes errors back',
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
// Score Bar Component
// ============================================================================

function ScoreBar({ label, score, maxScore = 10 }: { label: string; score: number | null; maxScore?: number }) {
  if (score === null || score === undefined) return null
  const percentage = (score / maxScore) * 100
  const getColor = (pct: number) => {
    if (pct >= 80) return 'bg-emerald-500'
    if (pct >= 60) return 'bg-indigo-500'
    if (pct >= 40) return 'bg-amber-500'
    return 'bg-red-400'
  }

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-stone-600">{label}</span>
        <span className="font-medium text-stone-900">{score.toFixed(1)}/10</span>
      </div>
      <div className="w-full bg-stone-100 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all ${getColor(percentage)}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

// ============================================================================
// Session Card Component
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

      {/* Status */}
      {isAnalyzing && (
        <div className="flex items-center gap-2 text-sm text-stone-500">
          <div className="animate-spin h-4 w-4 border-2 border-indigo-500 border-t-transparent rounded-full" />
          Analyzing your session with Claude...
        </div>
      )}

      {isFailed && (
        <div className="text-sm text-red-500 bg-red-50 rounded p-2">
          Analysis failed. Click "Retry" to try again.
        </div>
      )}

      {/* Results */}
      {isCompleted && session.builderScore !== undefined && (
        <div className="space-y-3">
          {/* Builder Score + Archetype */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-2xl font-bold text-stone-900">
                {session.builderScore.toFixed(1)}
              </div>
              <div className="text-sm text-stone-500">/10 Builder Score</div>
            </div>
            {archetype && (
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${archetype.color}`}>
                {archetype.label}
              </span>
            )}
          </div>

          {/* Summary */}
          {session.analysisSummary && (
            <p className="text-sm text-stone-600">{session.analysisSummary}</p>
          )}

          {/* Score Breakdown */}
          {session.scores && (
            <div className="space-y-2">
              <ScoreBar label="Direction & Intent" score={session.scores.direction} />
              <ScoreBar label="Design Thinking" score={session.scores.designThinking} />
              <ScoreBar label="Iteration Quality" score={session.scores.iterationQuality} />
              <ScoreBar label="Product Sense" score={session.scores.productSense} />
              <ScoreBar label="AI Leadership" score={session.scores.aiLeadership} />
            </div>
          )}

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-2 gap-3">
            {session.strengths && session.strengths.length > 0 && (
              <div>
                <h5 className="text-xs font-medium text-emerald-700 mb-1">Strengths</h5>
                <ul className="text-xs text-stone-600 space-y-0.5">
                  {session.strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-1">
                      <span className="text-emerald-500 mt-0.5">+</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {session.weaknesses && session.weaknesses.length > 0 && (
              <div>
                <h5 className="text-xs font-medium text-amber-700 mb-1">Areas to Improve</h5>
                <ul className="text-xs text-stone-600 space-y-0.5">
                  {session.weaknesses.map((w, i) => (
                    <li key={i} className="flex items-start gap-1">
                      <span className="text-amber-500 mt-0.5">-</span>
                      <span>{w}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
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
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileRead = useCallback((file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      setContent(text)
      // Auto-set title from filename
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
    // Reset form
    setContent('')
    setTitle('')
    setDescription('')
    setSource('')
    setProjectUrl('')
  }

  return (
    <div className="space-y-4">
      {/* Export Guides */}
      <div className="flex flex-wrap gap-2">
        <span className="text-sm text-stone-500">How to export from:</span>
        {Object.entries(EXPORT_GUIDES).map(([key, guide]) => (
          <button
            key={key}
            onClick={() => setShowGuide(showGuide === key ? null : key)}
            className={`text-xs px-2 py-1 rounded border transition-colors ${
              showGuide === key
                ? 'border-indigo-300 bg-indigo-50 text-indigo-700'
                : 'border-stone-200 text-stone-600 hover:border-stone-300'
            }`}
          >
            {guide.tool}
          </button>
        ))}
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

      {/* Drop Zone / Paste Area */}
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
          <div className="p-8 text-center">
            <div className="text-stone-400 mb-2">
              <svg className="mx-auto h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M9 8h6m-5 0a3 3 0 110 6H9l3 3m-3-6h6m6 1a9 9 0 11-18 0 9 9 0 0118 0z" />
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
            <p className="text-xs text-stone-400">
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
            <div className="mt-3 flex items-center gap-2 justify-center">
              <div className="h-px bg-stone-200 w-16" />
              <span className="text-xs text-stone-400">or paste directly</span>
              <div className="h-px bg-stone-200 w-16" />
            </div>
            <button
              onClick={async () => {
                try {
                  const text = await navigator.clipboard.readText()
                  if (text) setContent(text)
                } catch {
                  // Clipboard API not available - show textarea
                }
              }}
              className="mt-2 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Paste from clipboard
            </button>
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
            <pre className="text-xs text-stone-500 bg-white rounded p-2 max-h-32 overflow-y-auto border border-stone-100">
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
            <label className="text-xs text-stone-500 block mb-1">Description (optional)</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What did you build in this session?"
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
  const [bestScore, setBestScore] = useState<number | undefined>(initialData?.bestBuilderScore)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showUpload, setShowUpload] = useState(false)

  const refreshSessions = useCallback(async () => {
    try {
      const data = await vibeCodeApi.listSessions()
      setSessions(data.sessions)
      setBestScore(data.bestBuilderScore)
      onDataChange?.()
    } catch {
      // Silently fail on refresh
    }
  }, [onDataChange])

  const handleUpload = useCallback(async (data: Parameters<typeof vibeCodeApi.upload>[0]) => {
    setIsUploading(true)
    setError(null)
    try {
      const result = await vibeCodeApi.upload(data)
      // Add new session to list
      setSessions(prev => [result.session, ...prev])
      setShowUpload(false)

      // Poll for analysis completion
      const pollInterval = setInterval(async () => {
        try {
          const updated = await vibeCodeApi.listSessions()
          setSessions(updated.sessions)
          setBestScore(updated.bestBuilderScore)
          // Stop polling when analysis is done
          const session = updated.sessions.find(s => s.id === result.session.id)
          if (session && (session.analysisStatus === 'completed' || session.analysisStatus === 'failed')) {
            clearInterval(pollInterval)
          }
        } catch {
          clearInterval(pollInterval)
        }
      }, 5000)

      // Safety: stop polling after 3 minutes
      setTimeout(() => clearInterval(pollInterval), 180000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setIsUploading(false)
    }
  }, [])

  const handleDelete = useCallback(async (sessionId: string) => {
    try {
      await vibeCodeApi.deleteSession(sessionId)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      // Recalculate best score
      const remaining = sessions.filter(s => s.id !== sessionId && s.builderScore != null)
      setBestScore(remaining.length > 0 ? Math.max(...remaining.map(s => s.builderScore!)) : undefined)
    } catch {
      setError('Failed to delete session')
    }
  }, [sessions])

  const handleReanalyze = useCallback(async (sessionId: string) => {
    try {
      const updated = await vibeCodeApi.reanalyze(sessionId)
      setSessions(prev => prev.map(s => s.id === sessionId ? updated : s))
      // Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const data = await vibeCodeApi.listSessions()
          setSessions(data.sessions)
          setBestScore(data.bestBuilderScore)
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
              {bestScore !== undefined && (
                <span className="text-sm font-normal px-2 py-0.5 rounded-full bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700">
                  Best: {bestScore.toFixed(1)}/10
                </span>
              )}
            </CardTitle>
            <CardDescription>
              Upload your AI coding sessions (Cursor, Claude Code, Copilot) to show employers how you think and build
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
            <h4 className="text-sm font-medium text-stone-700 mb-1">No sessions uploaded yet</h4>
            <p className="text-xs text-stone-500 mb-4 max-w-sm mx-auto">
              Upload your AI coding sessions from Cursor, Claude Code, or Copilot.
              Employers will see how you think and build with AI tools.
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

        {/* Stats Summary */}
        {completedSessions.length >= 2 && (
          <div className="bg-stone-50 rounded-lg p-3 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-stone-900">{completedSessions.length}</div>
              <div className="text-xs text-stone-500">Sessions</div>
            </div>
            <div>
              <div className="text-lg font-bold text-stone-900">
                {bestScore?.toFixed(1) || '-'}
              </div>
              <div className="text-xs text-stone-500">Best Score</div>
            </div>
            <div>
              <div className="text-lg font-bold text-stone-900">
                {(completedSessions.reduce((sum, s) => sum + (s.builderScore || 0), 0) / completedSessions.length).toFixed(1)}
              </div>
              <div className="text-xs text-stone-500">Avg Score</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
