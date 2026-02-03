'use client'

import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'

interface AvailabilitySlot {
  dayOfWeek: number
  startTime: string
  endTime: string
}

interface AvailabilityGridProps {
  slots: AvailabilitySlot[]
  onChange: (slots: AvailabilitySlot[]) => void
  timezone?: string
  startHour?: number
  endHour?: number
  readOnly?: boolean
}

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const SHORT_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

function formatTime(hour: number): string {
  const h = hour % 12 || 12
  const ampm = hour < 12 ? 'AM' : 'PM'
  return `${h}${ampm}`
}

export function AvailabilityGrid({
  slots,
  onChange,
  timezone = 'America/Los_Angeles',
  startHour = 8,
  endHour = 20,
  readOnly = false,
}: AvailabilityGridProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState<{ day: number; hour: number } | null>(null)
  const [dragMode, setDragMode] = useState<'add' | 'remove'>('add')

  // Generate hours array
  const hours = []
  for (let h = startHour; h <= endHour; h++) {
    hours.push(h)
  }

  // Check if a time slot is selected
  const isSlotSelected = useCallback((day: number, hour: number): boolean => {
    const timeStr = `${hour.toString().padStart(2, '0')}:00`
    return slots.some(slot =>
      slot.dayOfWeek === day &&
      slot.startTime <= timeStr &&
      slot.endTime > timeStr
    )
  }, [slots])

  // Handle mouse down on a cell
  const handleMouseDown = (day: number, hour: number) => {
    if (readOnly) return
    setIsDragging(true)
    setDragStart({ day, hour })
    setDragMode(isSlotSelected(day, hour) ? 'remove' : 'add')
  }

  // Handle mouse enter while dragging
  const handleMouseEnter = (day: number, hour: number) => {
    if (!isDragging || !dragStart || readOnly) return

    // Only allow dragging within the same day
    if (day !== dragStart.day) return

    const minHour = Math.min(dragStart.hour, hour)
    const maxHour = Math.max(dragStart.hour, hour)

    const newSlots = [...slots]

    // Remove existing slots for this day that overlap
    const filteredSlots = newSlots.filter(s => s.dayOfWeek !== day)

    // Find existing slots for other days
    const otherDaySlots = slots.filter(s => s.dayOfWeek !== day)

    // Calculate new slots for this day
    const daySlots = slots.filter(s => s.dayOfWeek === day)

    if (dragMode === 'add') {
      // Add new slot
      const newStart = `${minHour.toString().padStart(2, '0')}:00`
      const newEnd = `${(maxHour + 1).toString().padStart(2, '0')}:00`

      // Merge with existing slots
      const mergedSlots = [...daySlots]
      let merged = false

      for (let i = 0; i < mergedSlots.length; i++) {
        const slot = mergedSlots[i]
        // Check if new slot overlaps or is adjacent
        if (newEnd >= slot.startTime && newStart <= slot.endTime) {
          // Merge slots
          mergedSlots[i] = {
            ...slot,
            startTime: newStart < slot.startTime ? newStart : slot.startTime,
            endTime: newEnd > slot.endTime ? newEnd : slot.endTime,
          }
          merged = true
          break
        }
      }

      if (!merged) {
        mergedSlots.push({
          dayOfWeek: day,
          startTime: newStart,
          endTime: newEnd,
        })
      }

      onChange([...otherDaySlots, ...mergedSlots])
    } else {
      // Remove slot (keep parts outside the drag range)
      const removeStart = `${minHour.toString().padStart(2, '0')}:00`
      const removeEnd = `${(maxHour + 1).toString().padStart(2, '0')}:00`

      const remainingSlots: AvailabilitySlot[] = []

      for (const slot of daySlots) {
        if (slot.endTime <= removeStart || slot.startTime >= removeEnd) {
          // No overlap, keep the slot
          remainingSlots.push(slot)
        } else {
          // Split the slot if needed
          if (slot.startTime < removeStart) {
            remainingSlots.push({
              ...slot,
              endTime: removeStart,
            })
          }
          if (slot.endTime > removeEnd) {
            remainingSlots.push({
              ...slot,
              startTime: removeEnd,
            })
          }
        }
      }

      onChange([...otherDaySlots, ...remainingSlots])
    }
  }

  // Handle mouse up
  const handleMouseUp = () => {
    setIsDragging(false)
    setDragStart(null)
  }

  // Apply preset templates
  const applyTemplate = (template: 'weekdays' | 'alldays' | 'custom') => {
    if (readOnly) return

    let newSlots: AvailabilitySlot[] = []

    switch (template) {
      case 'weekdays':
        // 9 AM - 5 PM, Monday to Friday
        for (let day = 0; day < 5; day++) {
          newSlots.push({
            dayOfWeek: day,
            startTime: '09:00',
            endTime: '17:00',
          })
        }
        break
      case 'alldays':
        // 9 AM - 5 PM, all days
        for (let day = 0; day < 7; day++) {
          newSlots.push({
            dayOfWeek: day,
            startTime: '09:00',
            endTime: '17:00',
          })
        }
        break
      case 'custom':
        // Clear all
        newSlots = []
        break
    }

    onChange(newSlots)
  }

  return (
    <div
      className="select-none"
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      {/* Template buttons */}
      {!readOnly && (
        <div className="flex gap-2 mb-4">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => applyTemplate('weekdays')}
          >
            Weekdays 9-5
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => applyTemplate('alldays')}
          >
            All Days 9-5
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => applyTemplate('custom')}
          >
            Clear All
          </Button>
        </div>
      )}

      {/* Grid */}
      <div className="overflow-x-auto">
        <div className="grid gap-0 min-w-[600px]" style={{ gridTemplateColumns: `80px repeat(${DAYS.length}, 1fr)` }}>
          {/* Header row */}
          <div className="p-2 text-sm font-medium text-gray-500 text-center border-b">
            {timezone.split('/')[1]?.replace('_', ' ') || timezone}
          </div>
          {SHORT_DAYS.map((day, i) => (
            <div key={i} className="p-2 text-sm font-medium text-gray-700 text-center border-b">
              {day}
            </div>
          ))}

          {/* Time rows */}
          {hours.map((hour) => (
            <>
              <div key={`time-${hour}`} className="p-2 text-xs text-gray-500 text-right pr-3 border-r">
                {formatTime(hour)}
              </div>
              {DAYS.map((_, dayIndex) => {
                const selected = isSlotSelected(dayIndex, hour)
                return (
                  <div
                    key={`${dayIndex}-${hour}`}
                    className={`
                      h-8 border-b border-r cursor-pointer transition-colors
                      ${selected ? 'bg-stone-800 hover:bg-stone-700' : 'bg-white hover:bg-stone-50'}
                      ${readOnly ? 'cursor-default' : ''}
                    `}
                    onMouseDown={() => handleMouseDown(dayIndex, hour)}
                    onMouseEnter={() => handleMouseEnter(dayIndex, hour)}
                  />
                )
              })}
            </>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-4 text-sm text-stone-600">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-stone-800 rounded" />
          <span>Available</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-white border border-stone-200 rounded" />
          <span>Unavailable</span>
        </div>
        {!readOnly && (
          <span className="text-stone-400 ml-4">Click and drag to select time blocks</span>
        )}
      </div>
    </div>
  )
}
