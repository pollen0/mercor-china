'use client'

import { useState, useRef, useEffect } from 'react'

export interface SelectOption {
  value: string
  label: string
}

interface CustomSelectProps {
  value: string
  onChange: (value: string) => void
  options: SelectOption[]
  placeholder?: string
  disabled?: boolean
  className?: string
  triggerClassName?: string
  size?: 'sm' | 'md'
  searchable?: boolean
  searchPlaceholder?: string
}

export function CustomSelect({
  value,
  onChange,
  options,
  placeholder = 'Select...',
  disabled = false,
  className = '',
  triggerClassName = '',
  size = 'md',
  searchable = false,
  searchPlaceholder = 'Search...',
}: CustomSelectProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')
  const ref = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setIsOpen(false)
        setSearch('')
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Close on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }
  }, [isOpen])

  const selectedOption = options.find(o => o.value === value)
  const displayLabel = selectedOption?.label || placeholder
  const filteredOptions = searchable && search
    ? options.filter(o => o.label.toLowerCase().includes(search.toLowerCase()))
    : options

  const heightClass = size === 'sm' ? 'h-9' : 'h-10'
  const textClass = size === 'sm' ? 'text-sm' : 'text-sm'

  return (
    <div ref={ref} className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          w-full ${heightClass} px-3 flex items-center justify-between rounded-lg border
          border-stone-200 ${textClass} bg-white text-left
          hover:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-900/10
          transition-colors disabled:bg-stone-50 disabled:cursor-not-allowed
          ${triggerClassName}
        `}
      >
        <span className={value ? 'text-stone-900' : 'text-stone-400'}>
          {displayLabel}
        </span>
        <svg
          className={`w-4 h-4 text-stone-400 transition-transform flex-shrink-0 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-stone-200 rounded-lg shadow-lg py-1 max-h-60 overflow-auto">
          {searchable && (
            <div className="px-3 py-2 sticky top-0 bg-white border-b border-stone-100">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={searchPlaceholder}
                className="w-full text-sm border border-stone-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-stone-400"
                autoFocus
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          )}
          {filteredOptions.map(option => (
            <button
              key={option.value}
              type="button"
              onClick={() => {
                onChange(option.value)
                setIsOpen(false)
                setSearch('')
              }}
              className={`
                w-full px-3 py-2 text-left ${textClass} transition-colors
                ${value === option.value
                  ? 'bg-stone-50 text-stone-900 font-medium'
                  : 'text-stone-700 hover:bg-stone-50'
                }
              `}
            >
              {option.label}
            </button>
          ))}
          {filteredOptions.length === 0 && (
            <p className="px-3 py-2 text-sm text-stone-400">No matches found</p>
          )}
        </div>
      )}
    </div>
  )
}

// Status select variant with colored indicators
interface StatusOption {
  value: string
  label: string
  color: string
  bgColor: string
}

interface StatusSelectProps {
  value: string
  onChange: (value: string) => void
  options: StatusOption[]
  disabled?: boolean
  className?: string
}

export function StatusSelect({
  value,
  onChange,
  options,
  disabled = false,
  className = '',
}: StatusSelectProps) {
  const [isOpen, setIsOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const selectedOption = options.find(o => o.value === value)

  return (
    <div ref={ref} className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          w-full h-8 px-2 pr-7 flex items-center gap-2 rounded-lg border border-stone-200
          text-xs font-medium transition-colors
          ${selectedOption?.bgColor || 'bg-stone-100'} ${selectedOption?.color || 'text-stone-600'}
          hover:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-900/10
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
      >
        <span className={`w-2 h-2 rounded-full ${selectedOption?.bgColor?.replace('bg-', 'bg-') || 'bg-stone-400'}`}
          style={{
            backgroundColor: selectedOption?.color?.includes('stone') ? '#57534e' :
                           selectedOption?.color?.includes('blue') ? '#1d4ed8' :
                           selectedOption?.color?.includes('amber') ? '#b45309' :
                           selectedOption?.color?.includes('teal') ? '#0f766e' :
                           selectedOption?.color?.includes('red') ? '#b91c1c' :
                           selectedOption?.color?.includes('green') ? '#15803d' : '#57534e'
          }}
        />
        <span className="truncate">{selectedOption?.label || 'Select'}</span>
        <svg
          className={`absolute right-2 w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-full min-w-[140px] bg-white border border-stone-200 rounded-lg shadow-lg py-1 max-h-60 overflow-auto">
          {options.map(option => (
            <button
              key={option.value}
              type="button"
              onClick={() => {
                onChange(option.value)
                setIsOpen(false)
              }}
              className={`
                w-full px-3 py-2 text-left text-xs flex items-center gap-2 transition-colors
                ${value === option.value ? 'bg-stone-50 font-medium' : 'hover:bg-stone-50'}
              `}
            >
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{
                  backgroundColor: option.color?.includes('stone') ? '#57534e' :
                                 option.color?.includes('blue') ? '#1d4ed8' :
                                 option.color?.includes('amber') ? '#b45309' :
                                 option.color?.includes('teal') ? '#0f766e' :
                                 option.color?.includes('red') ? '#b91c1c' :
                                 option.color?.includes('green') ? '#15803d' : '#57534e'
                }}
              />
              <span className={option.color}>{option.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
