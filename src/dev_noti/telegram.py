from dataclasses import dataclass
from pathlib import Path

from telegram import Bot
from telegram.constants import ChatType

from .base import NotiBase


@dataclass(frozen=True)
class TelegramConfig:
    token: str
    username: str


class TelegramNoti(NotiBase):
    def __init__(self, app: str, config: TelegramConfig):
        super().__init__(app=app)
        self.config = config
        self.bot = Bot(token=config.token)
        self.username = config.username
        self.chat_id: int | None = None

    @classmethod
    def from_toml(cls, *, app: str, config: Path | str):
        import tomli

        KEY = "telegram"

        with open(config, "rb") as f:
            config_vals = tomli.load(f)
        assert KEY in config_vals, f"{KEY} not found in config"
        return cls(
            app=app,
            config=TelegramConfig(**config_vals[KEY]),
        )

    async def async_chat_id(self) -> int:
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
