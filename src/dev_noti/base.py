import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Self, final

from structlog.stdlib import get_logger


class NotiBase(ABC):
    def __init__(self, *, app: str):
        self.app = app
        self.log = get_logger().bind(
            type=type(self).__name__,
            app=self.app,
        )

    @classmethod
    def from_dict(cls, *, app: str, config: dict[str, Any]) -> Self:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def toml_key(cls) -> str:
        raise NotImplementedError

    @classmethod
    def from_toml(cls, *, app: str, config: Path | str):
        import tomllib

        KEY = cls.toml_key()

        with open(config, "rb") as f:
            config_vals = tomllib.load(f)
        assert KEY in config_vals, f"{KEY} not found in config"
        return cls.from_dict(app=app, config=config_vals[KEY])

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
