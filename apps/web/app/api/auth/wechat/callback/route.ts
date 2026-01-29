import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { getWeChatAccessToken, getWeChatUserInfo, verifyState, isWeChatConfigured } from '@/lib/wechat'
import { prisma } from '@/lib/prisma'

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const code = searchParams.get('code')
  const state = searchParams.get('state')

  // Check for errors from WeChat
  if (!code) {
    const error = searchParams.get('error') || 'No authorization code received'
    return NextResponse.redirect(new URL(`/login?error=${encodeURIComponent(error)}`, request.url))
  }

  // Check if WeChat is configured
  if (!isWeChatConfigured()) {
    return NextResponse.redirect(new URL('/login?error=WeChat+not+configured', request.url))
  }

  // Verify state to prevent CSRF
  const cookieStore = await cookies()
  const storedState = cookieStore.get('wechat_oauth_state')?.value

  if (!storedState || !state || !verifyState(state, storedState)) {
    return NextResponse.redirect(new URL('/login?error=Invalid+state+parameter', request.url))
  }

  // Clear the state cookie
  cookieStore.delete('wechat_oauth_state')

  try {
    // Exchange code for access token
    const tokenResponse = await getWeChatAccessToken(code)

    // Get user info
    const userInfo = await getWeChatUserInfo(tokenResponse.access_token, tokenResponse.openid)

    // Check if candidate exists with this WeChat openid
    let candidate = await prisma.candidate.findUnique({
      where: { wechatOpenId: userInfo.openid },
    })

    if (!candidate) {
      // Check if there's a candidate with matching unionid
      if (userInfo.unionid) {
        candidate = await prisma.candidate.findFirst({
          where: { wechatUnionId: userInfo.unionid },
        })

        if (candidate) {
          // Update existing candidate with openid
          candidate = await prisma.candidate.update({
            where: { id: candidate.id },
            data: { wechatOpenId: userInfo.openid },
          })
        }
      }
    }

    if (!candidate) {
      // Create new candidate from WeChat info
      candidate = await prisma.candidate.create({
        data: {
          name: userInfo.nickname || 'WeChat User',
          email: `wechat_${userInfo.openid}@placeholder.local`, // Placeholder email
          phone: '', // Will need to collect later
          wechatOpenId: userInfo.openid,
          wechatUnionId: userInfo.unionid,
          targetRoles: [],
        },
      })
    }

    // Create session token via API
    const tokenResponse2 = await fetch(`${API_BASE_URL}/api/auth/wechat-token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidate_id: candidate.id,
        openid: userInfo.openid,
      }),
    })

    if (tokenResponse2.ok) {
      const tokenData = await tokenResponse2.json()

      // Set auth cookie
      cookieStore.set('candidate_token', tokenData.token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 7 * 24 * 60 * 60, // 7 days
        path: '/',
      })

      // Store candidate info for client
      cookieStore.set('candidate_info', JSON.stringify({
        id: candidate.id,
        name: candidate.name,
        email: candidate.email,
        needsProfileCompletion: !candidate.phone,
      }), {
        httpOnly: false,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 7 * 24 * 60 * 60,
        path: '/',
      })
    }

    // Redirect to profile completion if phone is missing
    if (!candidate.phone) {
      return NextResponse.redirect(new URL('/complete-profile', request.url))
    }

    // Redirect to home or intended destination
    const returnTo = searchParams.get('return_to') || '/'
    return NextResponse.redirect(new URL(returnTo, request.url))
  } catch (error) {
    console.error('WeChat OAuth error:', error)
    const errorMessage = error instanceof Error ? error.message : 'Authentication failed'
    return NextResponse.redirect(
      new URL(`/login?error=${encodeURIComponent(errorMessage)}`, request.url)
    )
  }
}
