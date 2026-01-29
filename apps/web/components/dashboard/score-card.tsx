'use client'

interface ScoreCardProps {
  score: number
  maxScore?: number
  label?: string
  size?: 'sm' | 'md' | 'lg'
}

export function ScoreCard({ score, maxScore = 10, label, size = 'md' }: ScoreCardProps) {
  const percentage = (score / maxScore) * 100

  const getColor = () => {
    if (percentage >= 70) return { bg: 'bg-green-100', text: 'text-green-700', ring: 'stroke-green-500' }
    if (percentage >= 50) return { bg: 'bg-yellow-100', text: 'text-yellow-700', ring: 'stroke-yellow-500' }
    return { bg: 'bg-red-100', text: 'text-red-700', ring: 'stroke-red-500' }
  }

  const colors = getColor()

  const sizes = {
    sm: { container: 'w-16 h-16', text: 'text-lg', label: 'text-xs' },
    md: { container: 'w-24 h-24', text: 'text-2xl', label: 'text-sm' },
    lg: { container: 'w-32 h-32', text: 'text-4xl', label: 'text-base' },
  }

  const sizeConfig = sizes[size]
  const strokeWidth = size === 'sm' ? 4 : size === 'md' ? 6 : 8
  const radius = 45

  return (
    <div className="flex flex-col items-center">
      <div className={`relative ${sizeConfig.container}`}>
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            className={colors.ring}
            strokeDasharray={`${2 * Math.PI * radius}`}
            strokeDashoffset={`${2 * Math.PI * radius * (1 - percentage / 100)}`}
            style={{ transition: 'stroke-dashoffset 0.5s ease-in-out' }}
          />
        </svg>

        {/* Score text */}
        <div className={`absolute inset-0 flex items-center justify-center ${colors.bg} rounded-full m-2`}>
          <span className={`font-bold ${colors.text} ${sizeConfig.text}`}>
            {score.toFixed(1)}
          </span>
        </div>
      </div>

      {label && (
        <span className={`mt-2 text-gray-600 ${sizeConfig.label}`}>{label}</span>
      )}
    </div>
  )
}
