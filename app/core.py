import asyncio
import logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "ComprasGov"
    log_level: str = "INFO"
    hcaptcha_url: str = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras"
    max_concurrent_solvers: int = 5

settings = Settings()

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

CONCURRENCY_LIMITER = asyncio.Semaphore(settings.max_concurrent_solvers)