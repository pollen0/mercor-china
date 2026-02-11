'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { employerApi, type MatchAlert, type MatchAlertList, ApiError } from '@/lib/api'

interface MatchAlertsProps {
  limit?: number
  showViewAll?: boolean
  onAlertClick?: (alert: MatchAlert) => void
}

export function MatchAlerts({ limit = 5, showViewAll = true, onAlertClick }: MatchAlertsProps) {
  const [alerts, setAlerts] = useState<MatchAlert[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadAlerts()
  }, [limit])

  const loadAlerts = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await employerApi.getMatchAlerts({ limit })
      setAlerts(data.alerts)
      setUnreadCount(data.unreadCount)
      setTotal(data.total)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to load match alerts')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleAlertClick = async (alert: MatchAlert) => {
    // Mark as viewed if it's new
    if (alert.isNew) {
      try {
        await employerApi.markMatchViewed(alert.id)
        // Update local state
        setAlerts(prev => prev.map(a =>
          a.id === alert.id ? { ...a, isNew: false, status: 'IN_REVIEW' } : a
        ))
        setUnreadCount(prev => Math.max(0, prev - 1))
      } catch (err) {
        console.error('Failed to mark alert as viewed:', err)
      }
    }

    onAlertClick?.(alert)
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <svg className="w-5 h-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            New Matches
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="w-6 h-6 border-2 border-teal-200 border-t-teal-600 rounded-full animate-spin" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">New Matches</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-600">{error}</p>
          <Button variant="outline" size="sm" onClick={loadAlerts} className="mt-2">
            Retry
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <svg className="w-5 h-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            New Matches
            {unreadCount > 0 && (
              <span className="bg-teal-100 text-teal-700 text-xs font-medium px-2 py-0.5 rounded-full">
                {unreadCount} new
              </span>
            )}
          </CardTitle>
          {showViewAll && total > limit && (
            <Link href="/dashboard?tab=talent" className="text-sm text-teal-600 hover:text-teal-700">
              View all ({total})
            </Link>
          )}
        </div>
        <CardDescription>
          Candidates matching your job requirements
        </CardDescription>
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <div className="text-center py-6">
            <svg className="w-12 h-12 text-stone-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <p className="text-stone-500 text-sm">No matches yet</p>
            <p className="text-stone-400 text-xs mt-1">
              Create a job to start matching with candidates
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <Link
                key={alert.id}
                href={`/dashboard/talent-pool/${alert.candidate.id}`}
                onClick={() => handleAlertClick(alert)}
                className={`block p-3 rounded-lg border transition-colors ${
                  alert.isNew
                    ? 'bg-teal-50 border-teal-200 hover:bg-teal-100'
                    : 'bg-stone-50 border-stone-200 hover:bg-stone-100'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                      alert.isNew ? 'bg-teal-200 text-teal-700' : 'bg-stone-200 text-stone-600'
                    }`}>
                      <span className="text-sm font-semibold">
                        {alert.candidate.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-stone-900 truncate">
                          {alert.candidate.name}
                        </p>
                        {alert.isNew && (
                          <span className="w-2 h-2 bg-teal-500 rounded-full flex-shrink-0" />
                        )}
                      </div>
                      <p className="text-sm text-stone-500 truncate">
                        {alert.candidate.university || 'Unknown university'}
                        {alert.candidate.graduationYear && ` '${String(alert.candidate.graduationYear).slice(-2)}`}
                      </p>
                      {alert.jobTitle && (
                        <p className="text-xs text-stone-400 truncate mt-0.5">
                          For: {alert.jobTitle}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className={`text-lg font-semibold ${
                      alert.matchScore >= 80 ? 'text-teal-600' :
                      alert.matchScore >= 60 ? 'text-stone-700' :
                      'text-stone-600'
                    }`}>
                      {Math.round(alert.matchScore)}%
                    </div>
                    <p className="text-xs text-stone-400">
                      {formatTimeAgo(alert.createdAt)}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
