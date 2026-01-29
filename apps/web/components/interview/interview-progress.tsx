'use client'

interface InterviewProgressProps {
  currentQuestion: number
  totalQuestions: number
  completedQuestions: number[]
}

export function InterviewProgress({
  currentQuestion,
  totalQuestions,
  completedQuestions,
}: InterviewProgressProps) {
  const progress = (completedQuestions.length / totalQuestions) * 100

  return (
    <div className="space-y-3">
      {/* Progress label */}
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-slate-300">Progress</span>
        <span className="text-sm text-slate-400">
          {completedQuestions.length}/{totalQuestions} completed
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Step indicators with numbers */}
      <div className="flex justify-between gap-2 pt-1">
        {Array.from({ length: totalQuestions }, (_, i) => {
          const questionNum = i + 1
          const isCompleted = completedQuestions.includes(i)
          const isCurrent = currentQuestion === i

          return (
            <div
              key={i}
              className={`
                w-8 h-8 rounded-full flex items-center justify-center
                text-sm font-medium transition-all
                ${isCurrent ? 'ring-2 ring-emerald-400 ring-offset-2 ring-offset-slate-800' : ''}
                ${isCompleted
                  ? 'bg-emerald-500 text-white'
                  : isCurrent
                  ? 'bg-emerald-500 text-white'
                  : 'bg-slate-700 text-slate-400'
                }
              `}
            >
              {isCompleted ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                questionNum
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
