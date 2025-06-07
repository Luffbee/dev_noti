# %%
from dev_noti.dingtalk import DingTalkNoti
from dev_noti.telegram import TelegramNoti

# %%
dt_noti = DingTalkNoti.from_toml(app="test", config="./dev_noti.toml")
dt_noti.send("Hello, world!")

# %%
tg_noti = TelegramNoti.from_toml(config="./dev_noti.toml", app="test")
tg_noti.send("Hello, world!")
# %%
