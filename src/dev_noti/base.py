import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import final

from structlog.stdlib import get_logger


class NotiBase(ABC):
    def __init__(self, *, app: str):
        self.app = app
        self.log = get_logger().bind(
            type=type(self).__name__,
            app=self.app,
        )

    @abstractmethod
    async def _async_send(self, msg: str):
        raise NotImplementedError

    def wrap_msg(self, msg: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.app}:{now}: {msg}"

    @final
    async def async_send(self, msg: str):
        try:
            await self._async_send(self.wrap_msg(msg))
            self.log.debug("msg sent", msg=msg)
        except Exception as e:
            self.log.error("msg send failed", msg=msg, error=e)

    def send(self, msg: str):
        asyncio.run(self.async_send(msg))
