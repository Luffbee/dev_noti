from dataclasses import dataclass
from typing import Any

from .base import NotiBase


@dataclass(frozen=True)
class TelegramConfig:
    token: str
    username: str


class TelegramNoti(NotiBase):
    def __init__(self, app: str, config: TelegramConfig):
        from telegram import Bot

        super().__init__(app=app)
        self.config = config
        self.bot = Bot(token=config.token)
        self.username = config.username
        self.chat_id: int | None = None

    @classmethod
    def from_dict(cls, *, app: str, config: dict[str, Any]):
        return cls(
            app=app,
            config=TelegramConfig(**config),
        )

    @classmethod
    def toml_key(cls):
        return "telegram"

    async def async_chat_id(self) -> int:
        from telegram.constants import ChatType

        if self.chat_id is not None:
            return self.chat_id
        ret = await self.bot.get_updates()
        for m in ret:
            msg = m.message
            if (
                (not msg)
                or (msg.chat.type != ChatType.PRIVATE)
                or (msg.chat.username != self.username)
            ):
                continue
            self.log.info("found chat id", chat_id=msg.chat.id)
            self.chat_id = msg.chat.id
            return self.chat_id
        raise ValueError("No chat id found")

    async def _async_send(self, msg: str):
        await self.bot.send_message(chat_id=await self.async_chat_id(), text=msg)
