import asyncio
from datetime import datetime
from pathlib import Path

from async_lru import alru_cache
from structlog.stdlib import get_logger
from telegram import Bot
from telegram.constants import ChatType


class TGNoti:
    def __init__(self, *, token: str, username: str):
        self.bot = Bot(token=token)
        self.username = username
        self.log = get_logger(app="TGNoti").bind(username=username)

    @classmethod
    def from_toml(cls, fpath: Path):
        import tomli

        with open(fpath, "rb") as f:
            config = tomli.load(f)
        return cls(token=config["auth"]["token"], username=config["auth"]["username"])

    @alru_cache
    async def async_chat_id(self) -> int:
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
            return msg.chat.id
        raise ValueError("No chat id found")

    async def async_send(self, msg: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            await self.bot.send_message(
                chat_id=await self.async_chat_id(), text=f"{now}: {msg}"
            )
            self.log.debug("msg sent", msg=msg)
        except Exception as e:
            self.log.error("msg send failed", msg=msg, error=e)

    def send(self, msg: str):
        asyncio.run(self.async_send(msg))
