"""
WeChat Work API client for sending messages
"""

import httpx
from typing import Any

from app.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger("app.utils.wechat")


class WeChatClient:
    """
    WeChat Work (企业微信) API client
    """

    def __init__(self) -> None:
        self.corp_id = settings.wechat_corp_id
        self.app_secret = settings.wechat_app_secret
        self.agent_id = settings.wechat_agent_id
        self._access_token: str | None = None
        self._base_url = "https://qyapi.weixin.qq.com/cgi-bin"

    async def get_access_token(self) -> str:
        """
        Get WeChat access token

        Returns:
            Access token
        """
        if self._access_token:
            return self._access_token

        url = f"{self._base_url}/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.app_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            if data.get("errcode") == 0:
                self._access_token = data.get("access_token")
                return self._access_token  # type: ignore

            logger.error(
                "Failed to get WeChat access token",
                extra={"errcode": data.get("errcode"), "errmsg": data.get("errmsg")},
            )
            raise Exception(f"WeChat API error: {data.get('errmsg')}")

    async def send_text_message(
        self,
        to_user: str,
        content: str,
    ) -> dict[str, Any]:
        """
        Send text message to WeChat user

        Args:
            to_user: Recipient user ID
            content: Message content

        Returns:
            Response data
        """
        access_token = await self.get_access_token()
        url = f"{self._base_url}/message/send?access_token={access_token}"

        payload = {
            "touser": to_user,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {
                "content": content,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            data = response.json()

            if data.get("errcode") == 0:
                logger.info(
                    "Text message sent",
                    extra={"to_user": to_user, "msgid": data.get("msgid")},
                )
            else:
                logger.error(
                    "Failed to send text message",
                    extra={"errcode": data.get("errcode"), "errmsg": data.get("errmsg")},
                )

            return data

    async def send_image_message(
        self,
        to_user: str,
        media_id: str,
    ) -> dict[str, Any]:
        """
        Send image message to WeChat user

        Args:
            to_user: Recipient user ID
            media_id: WeChat media ID

        Returns:
            Response data
        """
        access_token = await self.get_access_token()
        url = f"{self._base_url}/message/send?access_token={access_token}"

        payload = {
            "touser": to_user,
            "msgtype": "image",
            "agentid": self.agent_id,
            "image": {
                "media_id": media_id,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            data = response.json()

            if data.get("errcode") == 0:
                logger.info(
                    "Image message sent",
                    extra={"to_user": to_user, "msgid": data.get("msgid")},
                )
            else:
                logger.error(
                    "Failed to send image message",
                    extra={"errcode": data.get("errcode"), "errmsg": data.get("errmsg")},
                )

            return data

    async def send_file_message(
        self,
        to_user: str,
        media_id: str,
    ) -> dict[str, Any]:
        """
        Send file message to WeChat user

        Args:
            to_user: Recipient user ID
            media_id: WeChat media ID

        Returns:
            Response data
        """
        access_token = await self.get_access_token()
        url = f"{self._base_url}/message/send?access_token={access_token}"

        payload = {
            "touser": to_user,
            "msgtype": "file",
            "agentid": self.agent_id,
            "file": {
                "media_id": media_id,
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            data = response.json()

            if data.get("errcode") == 0:
                logger.info(
                    "File message sent",
                    extra={"to_user": to_user, "msgid": data.get("msgid")},
                )
            else:
                logger.error(
                    "Failed to send file message",
                    extra={"errcode": data.get("errcode"), "errmsg": data.get("errmsg")},
                )

            return data

    async def upload_media(
        self,
        file_path: str,
        media_type: str = "file",
    ) -> dict[str, Any]:
        """
        Upload media file to WeChat

        Args:
            file_path: Local file path
            media_type: Media type (image, voice, video, file)

        Returns:
            Response data with media_id
        """
        access_token = await self.get_access_token()
        url = f"{self._base_url}/media/upload?access_token={access_token}&type={media_type}"

        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                files = {"media": f}
                response = await client.post(url, files=files)
                data = response.json()

                if data.get("errcode") == 0:
                    logger.info(
                        "Media uploaded",
                        extra={"media_type": media_type, "media_id": data.get("media_id")},
                    )
                else:
                    logger.error(
                        "Failed to upload media",
                        extra={"errcode": data.get("errcode"), "errmsg": data.get("errmsg")},
                    )

                return data


# Create singleton instance
wechat_client = WeChatClient()
