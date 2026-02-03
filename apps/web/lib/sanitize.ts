/**
 * XSS Sanitization utilities for user-generated content.
 * Uses DOMPurify to remove potentially dangerous HTML/JavaScript.
 */
import DOMPurify from 'dompurify'

/**
 * Sanitize HTML content for safe rendering.
 * Removes scripts, event handlers, and dangerous elements.
 */
export function sanitizeHtml(dirty: string | null | undefined): string {
  if (!dirty) return ''

  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: [
      'b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre'
    ],
    ALLOWED_ATTR: ['href', 'title', 'target', 'rel'],
    ALLOW_DATA_ATTR: false,
    ADD_ATTR: ['target'],
    FORBID_TAGS: ['script', 'style', 'iframe', 'form', 'input'],
    FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover'],
  })
}

/**
 * Strip all HTML tags, returning plain text.
 */
export function stripHtml(dirty: string | null | undefined): string {
  if (!dirty) return ''

  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
  })
}

/**
 * Sanitize a URL to prevent javascript: protocol attacks.
 */
export function sanitizeUrl(url: string | null | undefined): string {
  if (!url) return ''

  // Check for dangerous protocols
  const lowerUrl = url.toLowerCase().trim()
  if (
    lowerUrl.startsWith('javascript:') ||
    lowerUrl.startsWith('vbscript:') ||
    lowerUrl.startsWith('data:') ||
    lowerUrl.startsWith('file:')
  ) {
    console.warn('Blocked dangerous URL:', url.substring(0, 50))
    return ''
  }

  return url
}

/**
 * Sanitize text for display (escapes HTML entities).
 */
export function escapeHtml(text: string | null | undefined): string {
  if (!text) return ''

  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  }

  return text.replace(/[&<>"']/g, (char) => map[char])
}

/**
 * Sanitize user-provided name.
 */
export function sanitizeName(name: string | null | undefined): string {
  if (!name) return ''
  return stripHtml(name).trim().slice(0, 200)
}

/**
 * Sanitize user-provided bio or description.
 */
export function sanitizeDescription(text: string | null | undefined): string {
  if (!text) return ''
  return stripHtml(text).slice(0, 5000)
}

/**
 * Check if a string contains potentially dangerous content.
 */
export function containsDangerousContent(text: string): boolean {
  if (!text) return false

  const dangerous = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /<iframe/i,
    /<object/i,
    /<embed/i,
    /vbscript:/i,
  ]

  return dangerous.some(pattern => pattern.test(text))
}

/**
 * Safe JSON parse with sanitization.
 */
export function safeJsonParse<T>(json: string | null | undefined, fallback: T): T {
  if (!json) return fallback

  try {
    const parsed = JSON.parse(json)
    // Basic sanitization for string values
    if (typeof parsed === 'object' && parsed !== null) {
      return sanitizeObject(parsed) as T
    }
    return parsed
  } catch {
    return fallback
  }
}

/**
 * Recursively sanitize string values in an object.
 */
export function sanitizeObject<T extends object>(obj: T): T {
  if (Array.isArray(obj)) {
    return obj.map(item => {
      if (typeof item === 'string') {
        return stripHtml(item)
      }
      if (typeof item === 'object' && item !== null) {
        return sanitizeObject(item)
      }
      return item
    }) as T
  }

  const result: Record<string, unknown> = {}
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      result[key] = stripHtml(value)
    } else if (typeof value === 'object' && value !== null) {
      result[key] = sanitizeObject(value as object)
    } else {
      result[key] = value
    }
  }
  return result as T
}
