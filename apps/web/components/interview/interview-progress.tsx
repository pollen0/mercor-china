'use client'

interface InterviewProgressProps {
  currentQuestion: number
  totalQuestions: number
  completedQuestions: number[]
  onQuestionClick?: (questionIndex: number) => void
}

export function InterviewProgress({
  currentQuestion,
  totalQuestions,
  completedQuestions,
  onQuestionClick,
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
          className="h-full bg-gradient-to-r from-teal-500 to-teal-400 transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Step indicators with numbers */}
      <div className="flex justify-between gap-2 pt-1">
        {Array.from({ length: totalQuestions }, (_, i) => {
          const questionNum = i + 1
          const isCompleted = completedQuestions.includes(i)
          const isCurrent = currentQuestion === i
          const canNavigate = onQuestionClick && (isCompleted || i <= currentQuestion)

          return (
            <button
              key={i}
              onClick={() => canNavigate && onQuestionClick?.(i)}
              disabled={!canNavigate}
              className={`
                w-8 h-8 rounded-full flex items-center justify-center
                text-sm font-medium transition-all
                ${isCurrent ? 'ring-2 ring-teal-400 ring-offset-2 ring-offset-slate-800' : ''}
                ${isCompleted
                  ? 'bg-teal-500 text-white'
                  : isCurrent
                  ? 'bg-teal-500 text-white'
                  : 'bg-slate-700 text-slate-400'
                }
                ${canNavigate ? 'cursor-pointer hover:scale-110 hover:ring-2 hover:ring-teal-400/50' : 'cursor-default'}
              `}
              title={canNavigate ? `Go to question ${questionNum}${isCompleted ? ' (re-record)' : ''}` : undefined}
            >
              {isCompleted ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                questionNum
              )}
            </button>
          )
        })}
      </div>

      {/* Retake hint */}
      {onQuestionClick && completedQuestions.length > 0 && (
        <p className="text-xs text-slate-500 text-center">
          Click a completed question to re-record it
        </p>
      )}
    </div>
  )
}
