'use client'

import { useState } from 'react'
import type { TeamMember } from '@/lib/api'

interface InterviewerSelectProps {
  teamMembers: TeamMember[]
  selectedIds: string[]
  onChange: (ids: string[]) => void
  maxSelection?: number
  showLoadInfo?: boolean
}

export function InterviewerSelect({
  teamMembers,
  selectedIds,
  onChange,
  maxSelection,
  showLoadInfo = true,
}: InterviewerSelectProps) {
  const [search, setSearch] = useState('')

  // Filter team members by search
  const filteredMembers = teamMembers.filter(member =>
    member.isActive &&
    (member.name.toLowerCase().includes(search.toLowerCase()) ||
     member.email.toLowerCase().includes(search.toLowerCase()))
  )

  const toggleMember = (memberId: string) => {
    if (selectedIds.includes(memberId)) {
      onChange(selectedIds.filter(id => id !== memberId))
    } else {
      if (maxSelection && selectedIds.length >= maxSelection) {
        // Replace last selected if at max
        onChange([...selectedIds.slice(0, -1), memberId])
      } else {
        onChange([...selectedIds, memberId])
      }
    }
  }

  const getLoadStatus = (member: TeamMember): { color: string; text: string } => {
    const todayLoad = member.interviewsToday || 0
    const maxToday = member.maxInterviewsPerDay || 4

    if (todayLoad >= maxToday) {
      return { color: 'text-red-600 bg-red-50', text: 'At capacity today' }
    }
    if (todayLoad >= maxToday * 0.75) {
      return { color: 'text-amber-600 bg-amber-50', text: `${todayLoad}/${maxToday} today` }
    }
    return { color: 'text-teal-600 bg-teal-50', text: `${todayLoad}/${maxToday} today` }
  }

  return (
    <div className="space-y-3">
      {/* Search input */}
      <div className="relative">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search team members..."
          className="w-full px-3 py-2 border border-stone-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-stone-900/10 focus:border-stone-300"
        />
        {search && (
          <button
            onClick={() => setSearch('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Selection summary */}
      {selectedIds.length > 0 && (
        <div className="text-sm text-stone-600">
          {selectedIds.length} interviewer{selectedIds.length !== 1 ? 's' : ''} selected
          {maxSelection && <span className="text-stone-400"> (max {maxSelection})</span>}
        </div>
      )}

      {/* Team member list */}
      <div className="max-h-64 overflow-y-auto space-y-2">
        {filteredMembers.length === 0 ? (
          <p className="text-center text-stone-500 py-4">
            {search ? 'No team members match your search' : 'No team members available'}
          </p>
        ) : (
          filteredMembers.map(member => {
            const isSelected = selectedIds.includes(member.id)
            const loadStatus = showLoadInfo ? getLoadStatus(member) : null

            return (
              <button
                key={member.id}
                type="button"
                onClick={() => toggleMember(member.id)}
                className={`
                  w-full flex items-center gap-3 p-3 rounded-lg border transition-colors text-left
                  ${isSelected
                    ? 'border-stone-900 bg-stone-50'
                    : 'border-stone-200 hover:border-stone-300 hover:bg-stone-50'
                  }
                `}
              >
                {/* Checkbox indicator */}
                <div className={`
                  w-5 h-5 rounded flex items-center justify-center flex-shrink-0
                  ${isSelected ? 'bg-stone-900 text-white' : 'border-2 border-stone-300'}
                `}>
                  {isSelected && (
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>

                {/* Member info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-stone-900 truncate">{member.name}</span>
                    {member.googleCalendarConnected && (
                      <span className="text-xs text-teal-600" title="Calendar connected">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 16H6c-.55 0-1-.45-1-1V8h14v10c0 .55-.45 1-1 1z" />
                        </svg>
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-stone-500 truncate">{member.email}</span>
                    <span className="text-xs text-stone-400 capitalize">{member.role.replace('_', ' ')}</span>
                  </div>
                </div>

                {/* Load indicator */}
                {loadStatus && (
                  <div className={`text-xs px-2 py-1 rounded-full flex-shrink-0 ${loadStatus.color}`}>
                    {loadStatus.text}
                  </div>
                )}
              </button>
            )
          })
        )}
      </div>

      {/* Help text */}
      <p className="text-xs text-stone-400">
        {maxSelection === 1
          ? 'Select one interviewer for this scheduling link'
          : 'Select interviewers who will be available for bookings. Load balancing will distribute meetings automatically.'}
      </p>
    </div>
  )
}
