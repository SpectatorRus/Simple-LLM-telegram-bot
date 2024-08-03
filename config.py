from dataclasses import dataclass

from environs import Env


@dataclass
class Bot:
    token: str  # token for API


@dataclass
class Config:
    tg_bot: Bot
    gigachat_bot: Bot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=Bot(token=env('BOT_TOKEN')),
                  gigachat_bot=Bot(token=env('GigaChad_TOKEN')))
