'use client'

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
        return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">Shortlisted</span>
      case 'REJECTED':
        return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">Rejected</span>
      case 'HIRED':
        return <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">Hired</span>
      default:
        return <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full">Pending</span>
    }
  }

  return (
    <div
      className={`bg-white rounded-lg border p-4 ${
        onClick ? 'cursor-pointer hover:border-blue-300 hover:shadow-md transition-all' : ''
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
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
              <span className="text-blue-700 font-semibold text-lg">
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
                  className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
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
