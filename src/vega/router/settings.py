from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import WebsocketUrl, FilePath

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    stt_url: WebsocketUrl
    tts_url: WebsocketUrl
    agents_config_path: FilePath

