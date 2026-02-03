'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { candidateApi, type GitHubAnalysis as GitHubAnalysisType } from '@/lib/api'

interface GitHubAnalysisProps {
  hasGitHub: boolean
}

export function GitHubAnalysis({ hasGitHub }: GitHubAnalysisProps) {
  const [analysis, setAnalysis] = useState<GitHubAnalysisType | null>(null)
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    if (hasGitHub) {
      loadAnalysis()
    }
  }, [hasGitHub])

  const loadAnalysis = async () => {
    try {
      setLoading(true)
      const data = await candidateApi.getGitHubAnalysis()
      setAnalysis(data)
      setError(null)
    } catch (err) {
      // Analysis might not exist yet, that's ok
      console.log('No analysis found')
    } finally {
      setLoading(false)
    }
  }

  const runAnalysis = async () => {
    setAnalyzing(true)
    setError(null)
    try {
      const data = await candidateApi.analyzeGitHub()
      setAnalysis(data)
    } catch (err) {
      console.error('Failed to analyze GitHub:', err)
      setError('Failed to analyze GitHub. Please try again.')
    } finally {
      setAnalyzing(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-teal-600'
    if (score >= 6) return 'text-stone-700'
    if (score >= 4) return 'text-amber-600'
    return 'text-red-600'
  }

  const getScoreBarColor = (score: number) => {
    if (score >= 8) return 'bg-teal-500'
    if (score >= 6) return 'bg-stone-500'
    if (score >= 4) return 'bg-amber-500'
    return 'bg-red-500'
  }

  if (!hasGitHub) return null

  if (loading) {
    return (
      <div className="border-t pt-3 mt-3">
        <div className="flex items-center gap-2 text-sm text-stone-500">
          <div className="w-4 h-4 border-2 border-stone-200 border-t-stone-500 rounded-full animate-spin" />
          Loading analysis...
        </div>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="border-t pt-3 mt-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-stone-700">Code Analysis</p>
            <p className="text-xs text-stone-500">AI analysis of your GitHub activity</p>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={runAnalysis}
            disabled={analyzing}
            className="text-xs"
          >
            {analyzing ? (
              <>
                <div className="w-3 h-3 border-2 border-stone-200 border-t-stone-500 rounded-full animate-spin mr-2" />
                Analyzing...
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                Run Analysis
              </>
            )}
          </Button>
        </div>
        {error && <p className="text-xs text-red-500 mt-2">{error}</p>}
      </div>
    )
  }

  return (
    <div className="border-t pt-3 mt-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-left"
      >
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-stone-700">Code Analysis</p>
          <span className={`text-lg font-bold ${getScoreColor(analysis.overallScore)}`}>
            {analysis.overallScore.toFixed(1)}
          </span>
        </div>
        <svg
          className={`w-4 h-4 text-stone-400 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {expanded && (
        <div className="mt-3 space-y-4">
          {/* Score Breakdown */}
          <div className="space-y-2">
            {[
              { label: 'Originality', score: analysis.originalityScore, desc: 'Unique, self-driven projects' },
              { label: 'Activity', score: analysis.activityScore, desc: 'Consistent contributions' },
              { label: 'Depth', score: analysis.depthScore, desc: 'Code complexity & quality' },
              { label: 'Collaboration', score: analysis.collaborationScore, desc: 'Team contributions' },
            ].map(({ label, score, desc }) => (
              <div key={label}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-stone-600">{label}</span>
                  <span className={`font-medium ${getScoreColor(score)}`}>{score.toFixed(1)}</span>
                </div>
                <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${getScoreBarColor(score)}`}
                    style={{ width: `${(score / 10) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-stone-400 mt-0.5">{desc}</p>
              </div>
            ))}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-3 text-center">
            <div className="p-2 bg-stone-50 rounded-lg">
              <p className="text-lg font-semibold text-stone-900">{analysis.totalReposAnalyzed}</p>
              <p className="text-xs text-stone-500">Repos Analyzed</p>
            </div>
            <div className="p-2 bg-stone-50 rounded-lg">
              <p className="text-lg font-semibold text-stone-900">{analysis.totalCommits.toLocaleString()}</p>
              <p className="text-xs text-stone-500">Total Commits</p>
            </div>
            <div className="p-2 bg-stone-50 rounded-lg">
              <p className="text-lg font-semibold text-stone-900">{analysis.personalProjects}</p>
              <p className="text-xs text-stone-500">Personal Projects</p>
            </div>
            <div className="p-2 bg-stone-50 rounded-lg">
              <p className="text-lg font-semibold text-stone-900">{(analysis.organicCodeRatio * 100).toFixed(0)}%</p>
              <p className="text-xs text-stone-500">Organic Code</p>
            </div>
          </div>

          {/* Quality Indicators */}
          <div className="flex flex-wrap gap-2">
            {analysis.hasTests && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-teal-50 text-teal-700 rounded-full">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Has Tests
              </span>
            )}
            {analysis.hasCiCd && (
              <span className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-teal-50 text-teal-700 rounded-full">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                CI/CD
              </span>
            )}
            {analysis.primaryLanguages?.slice(0, 3).map(lang => (
              <span key={lang.language} className="text-xs px-2 py-1 bg-stone-100 text-stone-600 rounded-full">
                {lang.language}
              </span>
            ))}
          </div>

          {/* Flags */}
          {analysis.flags && analysis.flags.length > 0 && (
            <div className="p-2 bg-amber-50 border border-amber-100 rounded-lg">
              <p className="text-xs font-medium text-amber-700 mb-1">Notes</p>
              <ul className="text-xs text-amber-600 space-y-0.5">
                {analysis.flags.map((flag, i) => (
                  <li key={i}>• {flag.detail}{flag.repo ? ` (${flag.repo})` : ''}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Analyzed At */}
          {analysis.analyzedAt && (
            <p className="text-xs text-stone-400 text-center">
              Analyzed {new Date(analysis.analyzedAt).toLocaleDateString()}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  runAnalysis()
                }}
                className="ml-2 text-teal-600 hover:underline"
                disabled={analyzing}
              >
                {analyzing ? 'Analyzing...' : 'Re-analyze'}
              </button>
            </p>
          )}
        </div>
      )}
    </div>
  )
}
