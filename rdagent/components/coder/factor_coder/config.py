from pydantic_settings import BaseSettings, SettingsConfigDict


class DataScienceCoderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATA_SCIENCE_CODER_")
    
    # Add settings here

    def __init__(self, **data):
        super().__init__(**data)


