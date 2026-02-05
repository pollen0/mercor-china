/**
 * Authentication utilities for Pathway.
 *
 * Handles token storage in both localStorage (for API calls) and cookies (for SSR/middleware).
 * The middleware.ts uses cookies to check auth state during SSR.
 */

type TokenType = 'candidate' | 'employer'

interface TokenData {
  token: string
  refreshToken?: string
  expiresIn?: number
}

/**
 * Set auth tokens for a user type.
 * Stores in both localStorage (for API calls) and cookies (for middleware).
 */
export function setAuthTokens(type: TokenType, data: TokenData): void {
  if (typeof window === 'undefined') return

  const tokenKey = `${type}_token`
  const refreshKey = `${type}_refresh_token`

  // Store in localStorage for API calls
  localStorage.setItem(tokenKey, data.token)
  if (data.refreshToken) {
    localStorage.setItem(refreshKey, data.refreshToken)
  }

  // Store in cookies for middleware (SSR)
  // Access token: session cookie (cleared when browser closes) or short expiry
  const tokenExpiry = data.expiresIn
    ? new Date(Date.now() + data.expiresIn * 1000).toUTCString()
    : undefined

  document.cookie = `${tokenKey}=${data.token}; path=/; SameSite=Lax${tokenExpiry ? `; expires=${tokenExpiry}` : ''}`

  // Refresh token: longer expiry (30 days)
  if (data.refreshToken) {
    const refreshExpiry = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toUTCString()
    document.cookie = `${refreshKey}=${data.refreshToken}; path=/; SameSite=Lax; expires=${refreshExpiry}`
  }
}

/**
 * Clear auth tokens for a user type.
 * Removes from both localStorage and cookies.
 */
export function clearAuthTokens(type: TokenType): void {
  if (typeof window === 'undefined') return

  const tokenKey = `${type}_token`
  const refreshKey = `${type}_refresh_token`

  // Clear localStorage
  localStorage.removeItem(tokenKey)
  localStorage.removeItem(refreshKey)

  // Clear cookies by setting expiry to past
  document.cookie = `${tokenKey}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`
  document.cookie = `${refreshKey}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`
}

/**
 * Get auth token for a user type.
 */
export function getAuthToken(type: TokenType): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(`${type}_token`)
}

/**
 * Get refresh token for a user type.
 */
export function getRefreshToken(type: TokenType): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(`${type}_refresh_token`)
}

/**
 * Check if user is authenticated (has valid token).
 */
export function isAuthenticated(type: TokenType): boolean {
  return !!getAuthToken(type)
}

/**
 * Refresh the access token using the refresh token.
 * Returns the new access token or null if refresh failed.
 */
export async function refreshAccessToken(type: TokenType): Promise<string | null> {
  const refreshToken = getRefreshToken(type)
  if (!refreshToken) return null

  try {
    const endpoint = type === 'candidate' ? '/api/candidates/refresh' : '/api/employers/refresh'
    const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    const response = await fetch(`${apiBase}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!response.ok) {
      // Refresh token is invalid, clear tokens
      clearAuthTokens(type)
      return null
    }

    const data = await response.json()

    // Update tokens
    setAuthTokens(type, {
      token: data.token,
      refreshToken: data.refresh_token,
      expiresIn: data.expires_in || 3600,
    })

    return data.token
  } catch {
    clearAuthTokens(type)
    return null
  }
}

/**
 * Logout the user - clear tokens and optionally call server logout.
 */
export async function logout(type: TokenType, callServer = true): Promise<void> {
  if (callServer) {
    const token = getAuthToken(type)
    if (token) {
      try {
        const endpoint = type === 'candidate' ? '/api/candidates/logout' : '/api/employers/logout'
        const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

        await fetch(`${apiBase}${endpoint}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })
      } catch {
        // Ignore logout errors - still clear local tokens
      }
    }
  }

  clearAuthTokens(type)
}
