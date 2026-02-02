'use client'

import { Badge } from '@/components/ui/badge'
import { ScoreCard } from './score-card'

interface CandidateCardProps {
  name: string
  email: string
  targetRoles?: string[]
  score?: number
  status?: 'PENDING' | 'SHORTLISTED' | 'REJECTED' | 'HIRED'
  photoUrl?: string
  onClick?: () => void
}

export function CandidateCard({
  name,
  email,
  targetRoles,
  score,
  status,
  photoUrl,
  onClick,
}: CandidateCardProps) {
  const getStatusBadge = () => {
    switch (status) {
      case 'SHORTLISTED':
        return <Badge variant="success">Shortlisted</Badge>
      case 'REJECTED':
        return <Badge variant="error">Rejected</Badge>
      case 'HIRED':
        return <Badge variant="info">Hired</Badge>
      default:
        return <Badge variant="neutral">Pending</Badge>
    }
  }

  return (
    <div
      className={`bg-white rounded-xl border border-gray-200 p-4 transition-all duration-200 ${
        onClick ? 'cursor-pointer hover:border-teal-300 hover:shadow-soft-md' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-start gap-4">
        {/* Avatar */}
        <div className="flex-shrink-0">
          {photoUrl ? (
            <img
              src={photoUrl}
              alt={name}
              className="w-12 h-12 rounded-full object-cover"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center">
              <span className="text-teal-700 font-semibold text-lg">
                {name.charAt(0).toUpperCase()}
              </span>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-grow min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-semibold text-gray-900 truncate">{name}</h3>
            {status && getStatusBadge()}
          </div>

          <p className="text-sm text-gray-500 truncate">{email}</p>

          {targetRoles && targetRoles.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {targetRoles.slice(0, 3).map((role, index) => (
                <span
                  key={index}
                  className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-md"
                >
                  {role}
                </span>
              ))}
              {targetRoles.length > 3 && (
                <span className="px-2 py-0.5 text-xs text-gray-500">
                  +{targetRoles.length - 3} more
                </span>
              )}
            </div>
          )}
        </div>

        {/* Score */}
        {score !== undefined && (
          <div className="flex-shrink-0">
            <ScoreCard score={score} size="sm" />
          </div>
        )}
      </div>
    </div>
  )
}
