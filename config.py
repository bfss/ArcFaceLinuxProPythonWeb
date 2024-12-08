# -*- coding: utf-8 -*-
"""配置信息"""
from pydantic_settings import BaseSettings, SettingsConfigDict


# 环境变量
class Config(BaseSettings):
    app_id: str
    sdk_key: str
    active_key: str

    model_config = SettingsConfigDict(env_file=".env")

config = Config()
