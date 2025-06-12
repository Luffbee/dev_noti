from dataclasses import dataclass
from typing import Any

from .base import NotiBase


@dataclass(frozen=True)
class DingTalkBotConfig:
    oapi: str
    secret: str


class DingTalkNoti(NotiBase):
    def __init__(self, app: str, config: DingTalkBotConfig):
        super().__init__(app=app)
        self.config = config

    @classmethod
    def from_dict(cls, *, app: str, config: dict[str, Any]):
        return cls(
            app=app,
            config=DingTalkBotConfig(**config),
        )

    @classmethod
    def toml_key(cls):
        return "dingtalk"

    def get_sign(self):
        import base64
        import hashlib
        import hmac
        import time
        import urllib.parse

        timestamp = str(round(time.time() * 1000))
        secret_enc = self.config.secret.encode("utf-8")
        string_to_sign = "{}\n{}".format(timestamp, self.config.secret)
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    async def _async_send(self, msg: str):
        import aiohttp

        ts, sign = self.get_sign()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.config.oapi}&timestamp={ts}&sign={sign}",
                headers={"Content-Type": "application/json"},
                json={"msgtype": "text", "text": {"content": msg}},
            ) as resp:
                resp.raise_for_status()
