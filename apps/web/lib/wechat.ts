/**
 * WeChat OAuth helpers for the Chinese market
 *
 * Documentation: https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html
 */

const WECHAT_APP_ID = process.env.WECHAT_APP_ID || ''
const WECHAT_APP_SECRET = process.env.WECHAT_APP_SECRET || ''
const WECHAT_REDIRECT_URI = process.env.NEXT_PUBLIC_WECHAT_REDIRECT_URI || ''

// WeChat OAuth URLs
const WECHAT_AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/qrconnect'
const WECHAT_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
const WECHAT_USERINFO_URL = 'https://api.weixin.qq.com/sns/userinfo'

export interface WeChatTokenResponse {
  access_token: string
  expires_in: number
  refresh_token: string
  openid: string
  scope: string
  unionid?: string
  errcode?: number
  errmsg?: string
}

export interface WeChatUserInfo {
  openid: string
  nickname: string
  sex: number
  province: string
  city: string
  country: string
  headimgurl: string
  privilege: string[]
  unionid?: string
  errcode?: number
  errmsg?: string
}

/**
 * Generate WeChat OAuth authorization URL
 * This URL should be used to redirect users to WeChat for login
 */
export function getWeChatAuthUrl(state?: string): string {
  const params = new URLSearchParams({
    appid: WECHAT_APP_ID,
    redirect_uri: WECHAT_REDIRECT_URI,
    response_type: 'code',
    scope: 'snsapi_login',
    state: state || generateState(),
  })

  return `${WECHAT_AUTHORIZE_URL}?${params.toString()}#wechat_redirect`
}

/**
 * Exchange authorization code for access token
 */
export async function getWeChatAccessToken(code: string): Promise<WeChatTokenResponse> {
  const params = new URLSearchParams({
    appid: WECHAT_APP_ID,
    secret: WECHAT_APP_SECRET,
    code,
    grant_type: 'authorization_code',
  })

  const response = await fetch(`${WECHAT_ACCESS_TOKEN_URL}?${params.toString()}`)
  const data = await response.json()

  if (data.errcode) {
    throw new Error(`WeChat OAuth error: ${data.errmsg} (${data.errcode})`)
  }

  return data
}

/**
 * Get user info using access token
 */
export async function getWeChatUserInfo(accessToken: string, openid: string): Promise<WeChatUserInfo> {
  const params = new URLSearchParams({
    access_token: accessToken,
    openid,
    lang: 'zh_CN',
  })

  const response = await fetch(`${WECHAT_USERINFO_URL}?${params.toString()}`)
  const data = await response.json()

  if (data.errcode) {
    throw new Error(`WeChat user info error: ${data.errmsg} (${data.errcode})`)
  }

  return data
}

/**
 * Generate a random state parameter for CSRF protection
 */
export function generateState(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
}

/**
 * Verify state parameter to prevent CSRF attacks
 */
export function verifyState(receivedState: string, storedState: string): boolean {
  return receivedState === storedState
}

/**
 * Get WeChat QR code image URL for scanning
 * This is for scenarios where you want to display the QR code directly
 */
export function getWeChatQRCodeUrl(state?: string): string {
  const authUrl = getWeChatAuthUrl(state)
  // The authUrl itself will display a QR code when opened in a browser
  return authUrl
}

/**
 * Check if WeChat is configured
 */
export function isWeChatConfigured(): boolean {
  return Boolean(WECHAT_APP_ID && WECHAT_APP_SECRET && WECHAT_REDIRECT_URI)
}
