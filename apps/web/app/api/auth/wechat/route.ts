import { NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { getWeChatAuthUrl, generateState, isWeChatConfigured } from '@/lib/wechat'

export async function GET() {
  // Check if WeChat is configured
  if (!isWeChatConfigured()) {
    return NextResponse.json(
      { error: 'WeChat OAuth is not configured' },
      { status: 500 }
    )
  }

  // Generate state for CSRF protection
  const state = generateState()

  // Store state in cookie for verification
  const cookieStore = await cookies()
  cookieStore.set('wechat_oauth_state', state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 600, // 10 minutes
    path: '/',
  })

  // Generate auth URL and redirect
  const authUrl = getWeChatAuthUrl(state)

  return NextResponse.redirect(authUrl)
}
