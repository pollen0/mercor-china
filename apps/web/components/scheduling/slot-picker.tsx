'use client'

import { useState, useMemo } from 'react'
import { Button } from '@/components/ui/button'

interface TimeSlot {
  start: string
  end: string
}

interface SlotPickerProps {
  slots: TimeSlot[]
  selectedSlot: string | null
  onSelect: (slotStart: string) => void
  timezone?: string
  durationMinutes?: number
}

interface DaySlots {
  date: string
  dayName: string
  slots: TimeSlot[]
}

function formatDate(dateStr: string): { date: string; dayName: string } {
  const date = new Date(dateStr)
  const dayName = date.toLocaleDateString('en-US', { weekday: 'short' })
  const month = date.toLocaleDateString('en-US', { month: 'short' })
  const day = date.getDate()
  return {
    date: `${month} ${day}`,
    dayName,
  }
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })
}

export function SlotPicker({
  slots,
  selectedSlot,
  onSelect,
  timezone = 'America/Los_Angeles',
  durationMinutes = 30,
}: SlotPickerProps) {
  const [selectedDate, setSelectedDate] = useState<string | null>(null)

  // Group slots by date
  const slotsByDate = useMemo(() => {
    const grouped: Record<string, TimeSlot[]> = {}

    for (const slot of slots) {
      const date = new Date(slot.start).toDateString()
      if (!grouped[date]) {
        grouped[date] = []
      }
      grouped[date].push(slot)
    }

    // Convert to array and sort by date
    return Object.entries(grouped)
      .map(([dateStr, dateSlots]) => {
        const { date, dayName } = formatDate(dateSlots[0].start)
        return {
          dateKey: dateStr,
          date,
          dayName,
          slots: dateSlots.sort((a, b) =>
            new Date(a.start).getTime() - new Date(b.start).getTime()
          ),
        }
      })
      .sort((a, b) =>
        new Date(a.slots[0].start).getTime() - new Date(b.slots[0].start).getTime()
      )
  }, [slots])

  // Get slots for selected date
  const selectedDateSlots = useMemo(() => {
    if (!selectedDate) return slotsByDate[0]?.slots || []
    return slotsByDate.find(d => d.dateKey === selectedDate)?.slots || []
  }, [selectedDate, slotsByDate])

  // Auto-select first date if none selected
  const activeDate = selectedDate || slotsByDate[0]?.dateKey

  if (slots.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg font-medium mb-2">No available slots</p>
        <p className="text-sm">Please check back later or contact us for assistance.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Timezone notice */}
      <div className="text-sm text-stone-500 text-center">
        Times shown in {timezone.replace('_', ' ')}
      </div>

      {/* Date selector */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {slotsByDate.map(({ dateKey, date, dayName }) => (
          <button
            key={dateKey}
            onClick={() => setSelectedDate(dateKey)}
            className={`
              flex-shrink-0 px-4 py-3 rounded-lg text-center transition-colors
              ${activeDate === dateKey
                ? 'bg-stone-900 text-white'
                : 'bg-stone-100 text-stone-700 hover:bg-stone-200'
              }
            `}
          >
            <div className="text-xs font-medium opacity-80">{dayName}</div>
            <div className="text-sm font-medium">{date}</div>
          </button>
        ))}
      </div>

      {/* Time slots */}
      <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
        {selectedDateSlots.map((slot) => {
          const isSelected = selectedSlot === slot.start
          return (
            <button
              key={slot.start}
              onClick={() => onSelect(slot.start)}
              className={`
                py-2.5 px-2 rounded-lg text-sm font-medium transition-colors
                ${isSelected
                  ? 'bg-stone-900 text-white'
                  : 'bg-white border border-stone-200 text-stone-700 hover:border-stone-300 hover:bg-stone-50'
                }
              `}
            >
              {formatTime(slot.start)}
            </button>
          )
        })}
      </div>

      {/* Duration info */}
      {selectedSlot && (
        <div className="bg-stone-50 border border-stone-100 rounded-lg p-4 text-center">
          <p className="text-stone-900 font-medium">
            Selected: {formatTime(selectedSlot)} - {formatTime(new Date(new Date(selectedSlot).getTime() + durationMinutes * 60000).toISOString())}
          </p>
          <p className="text-stone-500 text-sm mt-1">
            {durationMinutes} minute interview
          </p>
        </div>
      )}
    </div>
  )
}
