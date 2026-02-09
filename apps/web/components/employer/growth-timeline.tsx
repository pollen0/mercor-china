'use client'

import { useState, useEffect } from 'react'
import { talentPoolApi, type GrowthTimelineResponse } from '@/lib/api'

interface GrowthTimelineProps {
  candidateId: string
  profileId?: string
}

const EVENT_ICONS: Record<string, JSX.Element> = {
  interview: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  ),
  document: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  github: (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
    </svg>
  ),
  profile: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  ),
}

function formatRelativeDate(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'today'
  if (diffDays === 1) return 'yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 14) return '1 week ago'
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  if (diffDays < 60) return '1 month ago'
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`
  return `${Math.floor(diffDays / 365)} year${Math.floor(diffDays / 365) > 1 ? 's' : ''} ago`
}

function DeltaIndicator({ delta }: { delta: number | null | undefined }) {
  if (delta === null || delta === undefined) return null

  const isPositive = delta > 0
  const display = isPositive ? `+${delta}` : delta.toString()

  return (
    <span className={`text-sm font-medium ${isPositive ? 'text-teal-600' : 'text-stone-500'}`}>
      {display}
    </span>
  )
}

export function GrowthTimeline({ candidateId, profileId }: GrowthTimelineProps) {
  const [timeline, setTimeline] = useState<GrowthTimelineResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState(false)
  const [timeRange, setTimeRange] = useState<'6m' | '1y' | '2y' | 'all'>('1y')

  useEffect(() => {
    loadTimeline()
  }, [candidateId, profileId, timeRange])

  const loadTimeline = async () => {
    try {
      setLoading(true)
      const id = profileId || candidateId
      const data = await talentPoolApi.getGrowthTimeline(id, timeRange)
      setTimeline(data)
      setError(null)
    } catch (err) {
      console.error('Failed to load growth timeline:', err)
      setError('Failed to load growth data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-stone-700 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          Growth Timeline
        </h4>
        <div className="flex items-center justify-center py-4">
          <div className="w-5 h-5 border-2 border-stone-200 border-t-stone-600 rounded-full animate-spin" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-stone-700 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          Growth Timeline
        </h4>
        <p className="text-xs text-stone-500">No growth data available</p>
      </div>
    )
  }

  if (!timeline) return null

  const { summary, events } = timeline
  const hasData = summary.total_interviews > 0 || summary.resume_versions_count > 0 || summary.github_connected

  if (!hasData) {
    return (
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-stone-700 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          Growth Timeline
        </h4>
        <p className="text-xs text-stone-500">No activity tracked yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-stone-700 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          Growth Timeline
        </h4>
        {events.length > 0 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-stone-500 hover:text-stone-700 transition-colors"
          >
            {expanded ? 'Hide details' : 'View timeline'}
          </button>
        )}
      </div>

      {/* Summary Row - Always Visible */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-stone-600">
        {summary.total_interviews > 0 && (
          <span className="flex items-center gap-1">
            <span className="text-stone-500">Interviews:</span>
            <span className="font-medium">{summary.total_interviews}</span>
            {summary.interview_score_change !== null && (
              <DeltaIndicator delta={summary.interview_score_change} />
            )}
          </span>
        )}
        {summary.github_connected && (
          <span className="flex items-center gap-1">
            <span className="text-stone-500">GitHub:</span>
            {summary.github_score_change !== null ? (
              <DeltaIndicator delta={summary.github_score_change} />
            ) : (
              <span className="text-xs px-1.5 py-0.5 rounded bg-teal-50 text-teal-700">Connected</span>
            )}
          </span>
        )}
        {summary.resume_versions_count > 0 && (
          <span className="flex items-center gap-1">
            <span className="text-stone-500">Resumes:</span>
            <span className="font-medium">{summary.resume_versions_count}</span>
          </span>
        )}
        {summary.skills_growth_count > 0 && (
          <span className="flex items-center gap-1">
            <span className="text-stone-500">Skills:</span>
            <span className="text-teal-600 font-medium">+{summary.skills_growth_count}</span>
          </span>
        )}
      </div>

      {/* Expanded Timeline */}
      {expanded && events.length > 0 && (
        <div className="mt-3 space-y-1">
          {/* Time Range Filter */}
          <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
            <span className="text-xs text-stone-400">Show:</span>
            {(['6m', '1y', '2y', 'all'] as const).map(range => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-2 py-0.5 text-xs rounded transition-colors ${
                  timeRange === range
                    ? 'bg-stone-900 text-white'
                    : 'text-stone-500 hover:bg-stone-100'
                }`}
              >
                {range === 'all' ? 'All' : range}
              </button>
            ))}
          </div>

          {/* Events List */}
          <div className="max-h-64 overflow-y-auto space-y-1 pt-2">
            {events.map((event, index) => (
              <div
                key={index}
                className="flex items-start gap-3 py-2 px-2 rounded hover:bg-stone-50 transition-colors"
              >
                {/* Icon */}
                <div className="w-6 h-6 rounded-full bg-stone-100 flex items-center justify-center text-stone-600 flex-shrink-0 mt-0.5">
                  {EVENT_ICONS[event.icon] || EVENT_ICONS.profile}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-stone-900 truncate">{event.title}</p>
                  {event.subtitle && (
                    <p className="text-xs text-stone-500 truncate">{event.subtitle}</p>
                  )}
                </div>

                {/* Delta & Date */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {event.delta !== null && event.delta !== undefined && (
                    <DeltaIndicator delta={event.delta} />
                  )}
                  {event.event_date && (
                    <span className="text-xs text-stone-400">
                      {formatRelativeDate(event.event_date)}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {events.length === 0 && (
            <p className="text-xs text-stone-400 text-center py-4">
              No events in this time period
            </p>
          )}
        </div>
      )}
    </div>
  )
}
