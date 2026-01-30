'use client'

interface MatchScoreCardProps {
  candidateName: string
  overallScore?: number
  interviewScore?: number
  skillsScore?: number
  experienceScore?: number
  locationMatch?: boolean
  reasoning?: string
  status: string
  onClick?: () => void
}

function ScoreIndicator({ score, label, maxScore = 10 }: { score?: number; label: string; maxScore?: number }) {
  if (score === undefined || score === null) {
    return (
      <div className="text-center">
        <div className="text-xs text-gray-400">{label}</div>
        <div className="text-sm font-medium text-gray-500">N/A</div>
      </div>
    )
  }

  const percentage = (score / maxScore) * 100
  const getColor = () => {
    if (percentage >= 80) return 'text-emerald-600'
    if (percentage >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="text-center">
      <div className="text-xs text-gray-400">{label}</div>
      <div className={`text-sm font-semibold ${getColor()}`}>
        {score.toFixed(1)}
      </div>
    </div>
  )
}

export function MatchScoreCard({
  candidateName,
  overallScore,
  interviewScore,
  skillsScore,
  experienceScore,
  locationMatch,
  reasoning,
  status,
  onClick
}: MatchScoreCardProps) {
  const getOverallColor = () => {
    if (!overallScore) return 'bg-gray-100 text-gray-600'
    if (overallScore >= 80) return 'bg-emerald-100 text-emerald-700'
    if (overallScore >= 60) return 'bg-yellow-100 text-yellow-700'
    return 'bg-red-100 text-red-700'
  }

  const getStatusBadge = () => {
    switch (status) {
      case 'SHORTLISTED':
        return <span className="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs rounded-full">Shortlisted</span>
      case 'REJECTED':
        return <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">Rejected</span>
      case 'HIRED':
        return <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full">Hired</span>
      default:
        return <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">Pending</span>
    }
  }

  return (
    <div
      className={`bg-white border rounded-lg p-4 ${onClick ? 'cursor-pointer hover:border-emerald-300 hover:shadow-sm transition-all' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-start gap-4">
        {/* Overall Score Circle */}
        <div className={`w-16 h-16 rounded-full flex flex-col items-center justify-center flex-shrink-0 ${getOverallColor()}`}>
          <span className="text-lg font-bold">
            {overallScore !== undefined ? Math.round(overallScore) : '—'}
          </span>
          <span className="text-[10px] uppercase tracking-wide">Score</span>
        </div>

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-gray-900 truncate">{candidateName}</h4>
            {getStatusBadge()}
          </div>

          {/* Score Breakdown */}
          <div className="grid grid-cols-4 gap-2 mb-2">
            <ScoreIndicator score={interviewScore} label="Interview" />
            <ScoreIndicator score={skillsScore} label="Skills" />
            <ScoreIndicator score={experienceScore} label="Experience" />
            <div className="text-center">
              <div className="text-xs text-gray-400">Location</div>
              <div className="text-sm">
                {locationMatch === undefined || locationMatch === null ? (
                  <span className="text-gray-500">N/A</span>
                ) : locationMatch ? (
                  <span className="text-emerald-600">
                    <svg className="w-4 h-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </span>
                ) : (
                  <span className="text-red-600">
                    <svg className="w-4 h-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Reasoning */}
          {reasoning && (
            <p className="text-xs text-gray-500 line-clamp-2">{reasoning}</p>
          )}
        </div>
      </div>
    </div>
  )
}
