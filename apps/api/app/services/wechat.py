"""
WeChat OAuth service for candidate authentication.

Supports both WeChat Web (PC) and WeChat Mini Program login.
"""
import httpx
from typing import Optional
from dataclasses import dataclass
from ..config import settings


@dataclass
class WeChatUserInfo:
    """User info returned from WeChat OAuth."""
    openid: str
    unionid: Optional[str] = None
    nickname: Optional[str] = None
    headimgurl: Optional[str] = None
    sex: Optional[int] = None
    province: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class WeChatOAuthService:
    """
    WeChat OAuth 2.0 authentication service.

    Flow:
    1. Frontend redirects user to WeChat authorization URL
    2. User authorizes, WeChat redirects back with code
    3. Backend exchanges code for access_token and openid
    4. Backend fetches user info (if scope includes snsapi_userinfo)
    5. Backend creates/updates candidate and returns JWT

    References:
    - Web OAuth: https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html
    - Mini Program: https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html
    """

    # WeChat API endpoints
    WEB_AUTH_URL = "https://open.weixin.qq.com/connect/qrconnect"
    ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
    USERINFO_URL = "https://api.weixin.qq.com/sns/userinfo"
    MINI_PROGRAM_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"

    def __init__(self):
        self.app_id = settings.wechat_app_id
        self.app_secret = settings.wechat_app_secret

    def is_configured(self) -> bool:
        """Check if WeChat OAuth is properly configured."""
        return bool(self.app_id and self.app_secret)

    def get_web_auth_url(
        self,
        redirect_uri: str,
        state: str = "",
        scope: str = "snsapi_login"
    ) -> str:
        """
        Generate WeChat Web OAuth authorization URL.

        Args:
            redirect_uri: URL to redirect after authorization (must be URL-encoded)
            state: Optional state parameter for CSRF protection
            scope: OAuth scope (snsapi_login for web)

        Returns:
            Authorization URL to redirect the user to
        """
        import urllib.parse

        params = {
            "appid": self.app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
        }

        query_string = urllib.parse.urlencode(params)
        return f"{self.WEB_AUTH_URL}?{query_string}#wechat_redirect"

    async def exchange_code_for_token(self, code: str) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from WeChat callback

        Returns:
            Dict with access_token, refresh_token, openid, etc.

        Raises:
            Exception if the request fails or returns an error
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self.ACCESS_TOKEN_URL,
                params={
                    "appid": self.app_id,
                    "secret": self.app_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                }
            )
            response.raise_for_status()
            data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"WeChat OAuth error: {data.get('errmsg', 'Unknown error')}")

            return data

    async def get_user_info(self, access_token: str, openid: str) -> WeChatUserInfo:
        """
        Fetch user info from WeChat.

        Args:
            access_token: Valid access token
            openid: User's OpenID

        Returns:
            WeChatUserInfo with user details
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self.USERINFO_URL,
                params={
                    "access_token": access_token,
                    "openid": openid,
                    "lang": "zh_CN",
                }
            )
            response.raise_for_status()
            data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"WeChat userinfo error: {data.get('errmsg', 'Unknown error')}")

            return WeChatUserInfo(
                openid=data["openid"],
                unionid=data.get("unionid"),
                nickname=data.get("nickname"),
                headimgurl=data.get("headimgurl"),
                sex=data.get("sex"),
                province=data.get("province"),
                city=data.get("city"),
                country=data.get("country"),
            )

    async def mini_program_login(self, js_code: str) -> dict:
        """
        WeChat Mini Program login using js_code.

        Args:
            js_code: Login code from wx.login()

        Returns:
            Dict with session_key, openid, unionid (if available)
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self.MINI_PROGRAM_CODE2SESSION_URL,
                params={
                    "appid": self.app_id,
                    "secret": self.app_secret,
                    "js_code": js_code,
                    "grant_type": "authorization_code",
                }
            )
            response.raise_for_status()
            data = response.json()

            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"Mini Program login error: {data.get('errmsg', 'Unknown error')}")

            return data

    async def authenticate(self, code: str, is_mini_program: bool = False) -> WeChatUserInfo:
        """
        Complete OAuth flow: exchange code and get user info.

        Args:
            code: Authorization code or Mini Program js_code
            is_mini_program: Whether this is a Mini Program login

        Returns:
            WeChatUserInfo with user details (may only have openid for Mini Program)
        """
        if is_mini_program:
            # Mini Program flow - only returns openid and session_key
            data = await self.mini_program_login(code)
            return WeChatUserInfo(
                openid=data["openid"],
                unionid=data.get("unionid"),
            )
        else:
            # Web OAuth flow - can get full user info
            token_data = await self.exchange_code_for_token(code)
            return await self.get_user_info(
                access_token=token_data["access_token"],
                openid=token_data["openid"],
            )


# Global instance
wechat_service = WeChatOAuthService()
