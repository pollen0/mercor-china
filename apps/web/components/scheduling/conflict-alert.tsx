'use client'

import { Button } from '@/components/ui/button'

interface Conflict {
  interviewerId: string
  interviewerName: string
  conflictType: string
  conflictStart: string
  conflictEnd: string
  description?: string
}

interface TimeSlot {
  start: string
  end: string
  interviewerId: string
  interviewerName?: string
}

interface ConflictAlertProps {
  hasConflicts: boolean
  conflicts: Conflict[]
  suggestedAlternatives?: TimeSlot[]
  onSelectAlternative?: (slot: TimeSlot) => void
  onDismiss?: () => void
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

function getConflictTypeLabel(type: string): string {
  switch (type) {
    case 'calendar':
      return 'Calendar Busy'
    case 'existing_interview':
      return 'Existing Interview'
    case 'unavailable':
      return 'Not Available'
    case 'exception':
      return 'Blocked Time'
    case 'not_found':
      return 'Not Found'
    default:
      return 'Conflict'
  }
}

function getConflictTypeColor(type: string): string {
  switch (type) {
    case 'calendar':
      return 'bg-blue-100 text-blue-700'
    case 'existing_interview':
      return 'bg-orange-100 text-orange-700'
    case 'unavailable':
      return 'bg-gray-100 text-gray-700'
    case 'exception':
      return 'bg-purple-100 text-purple-700'
    default:
      return 'bg-red-100 text-red-700'
  }
}

export function ConflictAlert({
  hasConflicts,
  conflicts,
  suggestedAlternatives,
  onSelectAlternative,
  onDismiss,
}: ConflictAlertProps) {
  if (!hasConflicts) {
    return null
  }

  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 className="font-semibold text-red-900">Scheduling Conflicts Detected</h3>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-500 hover:text-red-700"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Conflict list */}
      <div className="space-y-2">
        {conflicts.map((conflict, index) => (
          <div
            key={index}
            className="flex items-center gap-3 p-3 bg-white rounded-lg border border-red-100"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-medium text-gray-900">{conflict.interviewerName}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${getConflictTypeColor(conflict.conflictType)}`}>
                  {getConflictTypeLabel(conflict.conflictType)}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                {formatTime(conflict.conflictStart)} - {formatTime(conflict.conflictEnd)}
                {conflict.description && (
                  <span className="text-gray-400 ml-2">- {conflict.description}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Suggested alternatives */}
      {suggestedAlternatives && suggestedAlternatives.length > 0 && onSelectAlternative && (
        <div className="pt-3 border-t border-red-200">
          <h4 className="text-sm font-medium text-red-900 mb-2">
            Suggested alternatives:
          </h4>
          <div className="flex flex-wrap gap-2">
            {suggestedAlternatives.slice(0, 5).map((slot, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => onSelectAlternative(slot)}
                className="bg-white border-gray-200 hover:border-indigo-300 hover:bg-indigo-50"
              >
                {formatDateTime(slot.start)}
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
