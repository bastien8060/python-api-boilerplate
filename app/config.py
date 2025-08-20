from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    # GelDB Client configuration
    GEL_HOST: str
    GEL_PORT: int
    GEL_USER: str
    GEL_PASSWORD: str
    GEL_CLIENT_TLS_SECURITY: str
    # OIDC config
    KEYCLOAK_BASE_URL: AnyHttpUrl
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_ALLOWED_REDIRECTS: List[AnyHttpUrl] = []
    AUTH_BASE_DOMAIN: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
