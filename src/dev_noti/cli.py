import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import cappa

from dev_noti.dingtalk import DingTalkNoti
from dev_noti.telegram import TelegramNoti


@dataclass
class DevNoti:
    msg: str
    type: Annotated[str | None, cappa.Arg(long=True)] = None
    config: Annotated[str, cappa.Arg(long=True)] = "./dev_noti.toml"

    def __call__(self):
        config = Path(self.config)
        if not config.is_file():
            raise cappa.Exit(f"Config file {config} not found", code=1)
        with open(config, "rb") as f:
            config_vals = tomllib.load(f)
        noti_type = self.type or list(config_vals.keys())[0]
        noti_map = {t.toml_key(): t for t in [DingTalkNoti, TelegramNoti]}
        noti = noti_map[noti_type].from_dict(app="cli", config=config_vals[noti_type])
        noti.send(self.msg)


def main():
    cappa.invoke(DevNoti)
