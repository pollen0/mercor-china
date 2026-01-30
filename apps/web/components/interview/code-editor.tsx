'use client'

import { useState, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/loading'
import type { CodingChallenge, TestCase } from '@/lib/api'

// Lazy load Monaco editor to reduce initial bundle size
const Editor = dynamic(() => import('@monaco-editor/react'), {
  ssr: false,
  loading: () => (
    <div className="flex-1 flex items-center justify-center bg-slate-900">
      <div className="text-center">
        <Spinner size="lg" className="mx-auto mb-3 border-slate-500 border-t-brand-500" />
        <p className="text-sm text-slate-400">Loading editor...</p>
      </div>
    </div>
  ),
})

interface CodeEditorProps {
  challenge: CodingChallenge
  onSubmit: (code: string) => void
  isSubmitting: boolean
  isPractice?: boolean
}

export function CodeEditor({ challenge, onSubmit, isSubmitting, isPractice = false }: CodeEditorProps) {
  const [code, setCode] = useState(challenge.starterCode || '')
  const [activeTab, setActiveTab] = useState<'description' | 'tests'>('description')

  const handleEditorChange = useCallback((value: string | undefined) => {
    setCode(value || '')
  }, [])

  const handleSubmit = useCallback(() => {
    if (code.trim()) {
      onSubmit(code)
    }
  }, [code, onSubmit])

  // Get visible test cases (non-hidden)
  const visibleTests = challenge.testCases.filter(tc => !tc.hidden)
  const hiddenTestCount = challenge.testCases.filter(tc => tc.hidden).length

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-[650px]">
      {/* Problem Panel */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 flex flex-col overflow-hidden">
        {/* Tabs */}
        <div className="flex border-b border-slate-700">
          <button
            onClick={() => setActiveTab('description')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'description'
                ? 'bg-slate-700/50 text-white border-b-2 border-emerald-500'
                : 'text-slate-400 hover:text-white hover:bg-slate-700/30'
            }`}
          >
            Problem
          </button>
          <button
            onClick={() => setActiveTab('tests')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'tests'
                ? 'bg-slate-700/50 text-white border-b-2 border-emerald-500'
                : 'text-slate-400 hover:text-white hover:bg-slate-700/30'
            }`}
          >
            Test Cases
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'description' ? (
            <div className="space-y-4">
              {/* Title */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <h2 className="text-lg font-semibold text-white">
                    {challenge.titleZh || challenge.title}
                  </h2>
                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                    challenge.difficulty === 'easy'
                      ? 'bg-green-500/20 text-green-400'
                      : challenge.difficulty === 'medium'
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}>
                    {challenge.difficulty === 'easy' ? 'Easy' : challenge.difficulty === 'medium' ? 'Medium' : 'Hard'}
                  </span>
                </div>
                {challenge.title !== challenge.titleZh && challenge.titleZh && (
                  <p className="text-sm text-slate-400">{challenge.title}</p>
                )}
              </div>

              {/* Description */}
              <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                {challenge.descriptionZh || challenge.description}
              </div>

              {/* Time Limit */}
              <div className="flex items-center gap-2 text-xs text-slate-400 pt-2 border-t border-slate-700">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Time Limit: {challenge.timeLimitSeconds}s per test</span>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {visibleTests.map((test, i) => (
                <TestCaseCard key={i} test={test} index={i + 1} />
              ))}

              {hiddenTestCount > 0 && (
                <div className="bg-slate-700/30 rounded-lg p-3 text-sm text-slate-400 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                  <span>+ {hiddenTestCount} hidden test{hiddenTestCount > 1 ? 's' : ''}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Editor Panel */}
      <div className="flex flex-col bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        {/* Editor Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-slate-700">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm-.5 4.5h1v7h-1v-7zm.5 9.5a.75.75 0 110 1.5.75.75 0 010-1.5z"/>
            </svg>
            <span className="text-sm text-slate-400">Python 3.10</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCode(challenge.starterCode || '')}
            className="text-slate-400 hover:text-white"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Reset
          </Button>
        </div>

        {/* Monaco Editor */}
        <div className="flex-1">
          <Editor
            height="100%"
            language="python"
            theme="vs-dark"
            value={code}
            onChange={handleEditorChange}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4,
              insertSpaces: true,
              wordWrap: 'on',
              padding: { top: 16, bottom: 16 },
            }}
          />
        </div>

        {/* Submit Button */}
        <div className="p-4 border-t border-slate-700">
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !code.trim()}
            className={`w-full py-3 font-semibold ${
              isPractice
                ? 'bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50'
                : 'bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-600/50'
            }`}
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Running Tests...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Submit Code
              </span>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}

// Test Case Card Component
function TestCaseCard({ test, index }: { test: TestCase; index: number }) {
  return (
    <div className="bg-slate-700/30 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-sm font-medium text-slate-300">
          {test.name || `Test Case ${index}`}
        </span>
      </div>

      <div className="space-y-2 text-sm">
        <div>
          <span className="text-slate-400">Input: </span>
          <code className="bg-slate-900 px-2 py-0.5 rounded text-emerald-400 font-mono">
            {test.input}
          </code>
        </div>
        <div>
          <span className="text-slate-400">Expected: </span>
          <code className="bg-slate-900 px-2 py-0.5 rounded text-blue-400 font-mono">
            {test.expected}
          </code>
        </div>
      </div>
    </div>
  )
}
