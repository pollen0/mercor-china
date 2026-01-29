'use client'

interface QuestionCardProps {
  questionNumber: number
  totalQuestions: number
  text: string
  textZh?: string
}

export function QuestionCard({
  questionNumber,
  totalQuestions,
  text,
  textZh,
}: QuestionCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 sm:p-6 border-l-4 border-blue-600">
      <div className="flex items-center justify-between mb-3 sm:mb-4">
        <span className="text-xs sm:text-sm font-medium text-blue-600 bg-blue-50 px-2 sm:px-3 py-1 rounded-full">
          Question {questionNumber} of {totalQuestions}
        </span>
      </div>

      <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2 leading-snug">
        {text}
      </h2>

      {textZh && (
        <p className="text-base sm:text-lg text-gray-600 leading-relaxed">
          {textZh}
        </p>
      )}
    </div>
  )
}
