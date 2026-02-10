import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Route protection middleware for Pathway.
 *
 * This middleware handles authentication-based routing:
 * - Protected routes redirect to login if no auth token
 * - Auth routes redirect to dashboard if already logged in
 * - Public routes pass through
 *
 * Token storage:
 * - Tokens are stored in cookies for SSR compatibility
 * - Frontend also stores in localStorage for client-side API calls
 */

// Routes that require candidate authentication
const CANDIDATE_PROTECTED_ROUTES = [
  '/candidate/dashboard',
  '/candidate/settings',
  '/candidate/resume',
  '/interview/select',
  '/interview/start',
  '/practice',
]

// Routes that require employer authentication
const EMPLOYER_PROTECTED_ROUTES = [
  '/employer/dashboard',
  '/dashboard',  // New unified dashboard
]

// Auth routes - redirect to dashboard if already authenticated
const CANDIDATE_AUTH_ROUTES = [
  '/candidate/login',
  '/register',
]

const EMPLOYER_AUTH_ROUTES = [
  '/employer/login',
]

// Public routes that don't need any auth check
const PUBLIC_ROUTES = [
  '/',
  '/privacy',
  '/terms',
  '/verify-email',
  '/auth/github/callback',
  '/auth/google/callback',
  '/schedule',
]

function isProtectedCandidateRoute(pathname: string): boolean {
  return CANDIDATE_PROTECTED_ROUTES.some(route =>
    pathname === route || pathname.startsWith(route + '/')
  )
}

function isProtectedEmployerRoute(pathname: string): boolean {
  return EMPLOYER_PROTECTED_ROUTES.some(route =>
    pathname === route || pathname.startsWith(route + '/')
  )
}

function isInterviewRoute(pathname: string): boolean {
  // Interview room routes like /interview/[sessionId]/room
  return /^\/interview\/[^/]+\/(room|complete)/.test(pathname)
}

function isCandidateAuthRoute(pathname: string): boolean {
  return CANDIDATE_AUTH_ROUTES.some(route => pathname === route)
}

function isEmployerAuthRoute(pathname: string): boolean {
  return EMPLOYER_AUTH_ROUTES.some(route => pathname === route)
}

function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.some(route =>
    pathname === route || pathname.startsWith(route + '/')
  )
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Skip middleware for static files and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') // Static files
  ) {
    return NextResponse.next()
  }

  // Get auth tokens from cookies
  const candidateToken = request.cookies.get('candidate_token')?.value
  const employerToken = request.cookies.get('employer_token')?.value

  // Check if this is a protected candidate route
  if (isProtectedCandidateRoute(pathname) || isInterviewRoute(pathname)) {
    if (!candidateToken) {
      // Redirect to login with return URL
      const loginUrl = new URL('/candidate/login', request.url)
      loginUrl.searchParams.set('returnTo', pathname)
      return NextResponse.redirect(loginUrl)
    }
    return NextResponse.next()
  }

  // Check if this is a protected employer route
  if (isProtectedEmployerRoute(pathname)) {
    if (!employerToken) {
      // Redirect to employer login with return URL
      const loginUrl = new URL('/employer/login', request.url)
      loginUrl.searchParams.set('returnTo', pathname)
      return NextResponse.redirect(loginUrl)
    }
    return NextResponse.next()
  }

  // Check if already authenticated and trying to access auth routes
  if (isCandidateAuthRoute(pathname)) {
    if (candidateToken) {
      // Already logged in, redirect to dashboard
      return NextResponse.redirect(new URL('/candidate/dashboard', request.url))
    }
    return NextResponse.next()
  }

  if (isEmployerAuthRoute(pathname)) {
    if (employerToken) {
      // Already logged in, redirect to talent pool (default employer view)
      return NextResponse.redirect(new URL('/dashboard?tab=talent', request.url))
    }
    return NextResponse.next()
  }

  // Public routes and everything else passes through
  return NextResponse.next()
}

// Configure which routes the middleware runs on
export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
}
