'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { candidateNotesApi, type CandidateNote } from '@/lib/api'

interface CandidateNotesProps {
  candidateId: string
  candidateName?: string
}

export function CandidateNotes({ candidateId, candidateName }: CandidateNotesProps) {
  const [notes, setNotes] = useState<CandidateNote[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newNote, setNewNote] = useState('')
  const [saving, setSaving] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  const [deletingId, setDeletingId] = useState<string | null>(null)

  useEffect(() => {
    loadNotes()
  }, [candidateId])

  const loadNotes = async () => {
    try {
      setLoading(true)
      const { notes: data } = await candidateNotesApi.list(candidateId)
      setNotes(data)
      setError(null)
    } catch (err) {
      console.error('Failed to load notes:', err)
      setError('Failed to load notes')
    } finally {
      setLoading(false)
    }
  }

  const handleAddNote = async () => {
    if (!newNote.trim()) return

    setSaving(true)
    try {
      const note = await candidateNotesApi.create(candidateId, newNote.trim())
      setNotes([note, ...notes])
      setNewNote('')
      setError(null)
    } catch (err) {
      console.error('Failed to add note:', err)
      setError('Failed to add note')
    } finally {
      setSaving(false)
    }
  }

  const handleUpdateNote = async (noteId: string) => {
    if (!editContent.trim()) return

    setSaving(true)
    try {
      const updated = await candidateNotesApi.update(candidateId, noteId, editContent.trim())
      setNotes(notes.map(n => n.id === noteId ? updated : n))
      setEditingId(null)
      setEditContent('')
      setError(null)
    } catch (err) {
      console.error('Failed to update note:', err)
      setError('Failed to update note')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteNote = async (noteId: string) => {
    if (!confirm('Are you sure you want to delete this note?')) return

    setDeletingId(noteId)
    try {
      await candidateNotesApi.delete(candidateId, noteId)
      setNotes(notes.filter(n => n.id !== noteId))
      setError(null)
    } catch (err) {
      console.error('Failed to delete note:', err)
      setError('Failed to delete note')
    } finally {
      setDeletingId(null)
    }
  }

  const startEditing = (note: CandidateNote) => {
    setEditingId(note.id)
    setEditContent(note.content)
  }

  const cancelEditing = () => {
    setEditingId(null)
    setEditContent('')
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-stone-700 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          Notes
        </h4>
        <div className="flex items-center justify-center py-4">
          <div className="w-5 h-5 border-2 border-stone-200 border-t-stone-500 rounded-full animate-spin" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-stone-700 flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        Notes
        {notes.length > 0 && (
          <span className="text-xs text-stone-400 font-normal">({notes.length})</span>
        )}
      </h4>

      {error && (
        <p className="text-xs text-red-600">{error}</p>
      )}

      {/* Add Note Form */}
      <div className="space-y-2">
        <textarea
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
          placeholder={`Add a private note about ${candidateName || 'this candidate'}...`}
          rows={2}
          className="w-full px-3 py-2 text-sm border border-stone-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none"
          onClick={(e) => e.stopPropagation()}
        />
        <Button
          size="sm"
          onClick={(e) => {
            e.stopPropagation()
            handleAddNote()
          }}
          disabled={saving || !newNote.trim()}
          className="bg-stone-900 hover:bg-stone-800 text-xs"
        >
          {saving ? 'Adding...' : 'Add Note'}
        </Button>
      </div>

      {/* Notes List */}
      {notes.length > 0 && (
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {notes.map(note => (
            <div
              key={note.id}
              className="p-2 bg-white border border-stone-200 rounded-lg"
              onClick={(e) => e.stopPropagation()}
            >
              {editingId === note.id ? (
                <div className="space-y-2">
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    rows={2}
                    className="w-full px-2 py-1 text-sm border border-stone-200 rounded focus:ring-2 focus:ring-teal-500 focus:border-teal-500 resize-none"
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-xs"
                      onClick={cancelEditing}
                      disabled={saving}
                    >
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      className="text-xs bg-stone-900 hover:bg-stone-800"
                      onClick={() => handleUpdateNote(note.id)}
                      disabled={saving || !editContent.trim()}
                    >
                      {saving ? 'Saving...' : 'Save'}
                    </Button>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-sm text-stone-700 whitespace-pre-wrap">{note.content}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-stone-400">{formatDate(note.createdAt)}</span>
                    <div className="flex gap-1">
                      <button
                        onClick={() => startEditing(note)}
                        className="p-1 text-stone-400 hover:text-stone-600 hover:bg-stone-50 rounded transition-colors"
                        title="Edit"
                      >
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDeleteNote(note.id)}
                        disabled={deletingId === note.id}
                        className="p-1 text-stone-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                        title="Delete"
                      >
                        {deletingId === note.id ? (
                          <div className="w-3.5 h-3.5 border-2 border-stone-200 border-t-red-500 rounded-full animate-spin" />
                        ) : (
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}

      {notes.length === 0 && (
        <p className="text-xs text-stone-400 italic">No notes yet. Add your first note above.</p>
      )}
    </div>
  )
}
