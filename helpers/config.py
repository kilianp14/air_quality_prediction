from pathlib import Path
import os
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class HopsworksSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    MLFS_DIR: Path = Path(__file__).parent

    # For hopsworks.login(), set as environment variables if they are not already set as env variables
    HOPSWORKS_API_KEY: SecretStr | None = None
    HOPSWORKS_PROJECT: str | None = None
    HOPSWORKS_HOST: str | None = None

    # Air Quality
    AQICN_API_KEY: SecretStr | None = None
    AQICN_COUNTRIES: list[str] | None = None
    AQICN_CITIES: list[str] | None = None
    AQICN_STREETS: list[str] | None = None
    AQICN_URLS: list[str] | None = None

    # Other API Keys
    OPENAI_MODEL_ID: str = "gpt-4o-mini"

    @field_validator('AQICN_COUNTRIES', 'AQICN_CITIES', 'AQICN_STREETS', 'AQICN_URLS', mode='before')
    def split_comma_separated(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v

    def model_post_init(self, __context):
        print("HopsworksSettings initialized!")

        # Set environment variables if not already set
        if os.getenv("HOPSWORKS_API_KEY") is None and self.HOPSWORKS_API_KEY is not None:
            os.environ['HOPSWORKS_API_KEY'] = self.HOPSWORKS_API_KEY.get_secret_value()
        if os.getenv("HOPSWORKS_PROJECT") is None and self.HOPSWORKS_PROJECT is not None:
            os.environ['HOPSWORKS_PROJECT'] = self.HOPSWORKS_PROJECT
        if os.getenv("HOPSWORKS_HOST") is None and self.HOPSWORKS_HOST is not None:
            os.environ['HOPSWORKS_HOST'] = self.HOPSWORKS_HOST

        # --- Check required .env values ---
        missing = []

        if not self.HOPSWORKS_API_KEY:
            missing.append("HOPSWORKS_API_KEY")
        if not self.AQICN_API_KEY:
            missing.append("AQICN_API_KEY")
        if not self.AQICN_COUNTRIES:
            missing.append("AQICN_COUNTRIES")
        if not self.AQICN_CITIES:
            missing.append("AQICN_CITIES")
        if not self.AQICN_STREETS:
            missing.append("AQICN_STREETS")
        if not self.AQICN_URLS:
            missing.append("AQICN_URLS")

        if missing:
            raise ValueError(
                "The following required settings are missing from your environment (.env or system):\n  " +
                "\n  ".join(missing)
            )
