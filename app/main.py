import asyncio
import logging
import os
import time
from typing import Optional
import undetected_chromedriver as uc
from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class Settings(BaseSettings):
    app_name: str = "hCaptcha Solver API"
    log_level: str = "INFO"
    hcaptcha_url: str = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras"
    max_concurrent_solvers: int = 3


settings = Settings()


logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)



class StatusResponse(BaseModel):
    status: str = Field(..., example="ok", description="Status da API")


class HCaptchaResponse(BaseModel):
    hcaptcha_token: str = Field(..., example="P1_eyJ...U5Z", description="Token hCaptcha resolvido")


class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Não foi possível capturar o hCaptcha.")


CONCURRENCY_LIMITER = asyncio.Semaphore(settings.max_concurrent_solvers)




def _atualizar_chrome():
    """Força a atualização do Google Chrome usando o winget (para Windows)."""
    logger.info("Tentando atualizar o Google Chrome via winget...")
    cmd = (
        "winget install --id Google.Chrome.EXE --exact "
        "--silent --accept-source-agreements --accept-package-agreements"
    )
    retorno = os.system(cmd)
    if retorno == 0:
        logger.info("Google Chrome atualizado/reinstalado com sucesso!")
    else:
        logger.warning(f"Falha ao atualizar o Google Chrome (código de saída: {retorno})")


def solve_hcaptcha_sync(max_attempts: int = 3) -> Optional[str]:
    """
    Função SÍNCRONA e BLOQUEANTE que executa a lógica do Selenium.
    Esta função será executada em um thread separado para não bloquear a API.
    """
    driver: Optional[uc.Chrome] = None
    for attempt in range(1, max_attempts + 1):
        logger.info(f"Tentativa {attempt} de {max_attempts} para resolver o hCaptcha...")

        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--incognito")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless=new")
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        )
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.accept_insecure_certs = True


        try:
            driver = uc.Chrome(options=options)
            driver.get(settings.hcaptcha_url)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-hcaptcha-widget-id]"))
            )
            logger.info("hCaptcha carregado com sucesso.")

            widget_id_element = driver.find_element(By.CSS_SELECTOR, '[data-hcaptcha-widget-id]')
            widget_id = widget_id_element.get_attribute('data-hcaptcha-widget-id')
            logger.info(f"Widget ID encontrado: {widget_id}")

            driver.execute_script(f"hcaptcha.execute('{widget_id}');")
            logger.info("Script hcaptcha.execute() injetado.")


            token = WebDriverWait(driver, 25).until(
                lambda d: d.execute_script(f"return hcaptcha.getResponse('{widget_id}');")
            )

            if token:
                logger.info("Token hCaptcha obtido com sucesso.")
                return token
            else:
                logger.warning("Token recebido está vazio. Tentando novamente.")
                continue

        except SessionNotCreatedException as e:
            logger.error(f"Erro ao criar a sessão do driver: {e}")
            logger.info("Tentando atualizar o Google Chrome e reiniciar...")
            _atualizar_chrome()

        except TimeoutException:
            logger.error(f"Erro na tentativa {attempt}: Tempo esgotado ao esperar por um elemento do hCaptcha.")

        except Exception as e:
            logger.error(f"Ocorreu um erro inesperado na tentativa {attempt}: {e}", exc_info=True)

        finally:
            if driver:
                driver.quit()
            # Garante que os processos sejam limpos, mesmo em caso de erro.
            #_kill_chrome_processes(driver)

        if attempt < max_attempts:
            logger.info("Aguardando 2 segundos antes da próxima tentativa...")
            time.sleep(2)

    logger.error("Todas as tentativas de resolver o hCaptcha falharam.")
    return None



router = APIRouter(
    prefix="/api/v1",
    tags=["hCaptcha Solver"]
)


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Verifica o status da API",
)
async def get_status():
    """Endpoint simples para verificar se a API está online."""
    return {"status": "ok"}


@router.get(
    "/get_hcaptcha",
    response_model=HCaptchaResponse,
    summary="Obtém um token hCaptcha",
    responses={
        500: {"model": ErrorResponse, "description": "Falha ao obter o token"},
        503: {"model": ErrorResponse, "description": "Serviço indisponível (muitas requisições)"}
    }
)
async def get_hcaptcha_token():
    """
    Inicia o processo para resolver o hCaptcha na URL configurada.
    Esta operação é intensiva e limitada a um número de três execuções concorrentes.
    Com o token retornado é possível acessar diversos endpoints do portal ComprasGov
    """
    try:
        async with asyncio.timeout(0.1):
            await CONCURRENCY_LIMITER.acquire()
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O serviço está ocupado. Tente novamente mais tarde."
        )

    try:
        logger.info("Iniciando processo de resolução de hCaptcha em um thread separado.")
        token = await asyncio.to_thread(solve_hcaptcha_sync)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Não foi possível capturar o hCaptcha após múltiplas tentativas"
            )

        return HCaptchaResponse(hcaptcha_token=token)

    except Exception as e:
        logger.error(f"Erro não tratado no endpoint /get_hcaptcha: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno inesperado."
        )
    finally:

        CONCURRENCY_LIMITER.release()
        logger.info("Slot de execução de hCaptcha liberado.")



app = FastAPI(
    title=settings.app_name,
    description="API para resolver hCaptcha usando Selenium e Undetected Chromedriver.",
    version="1.0.0"
)

app.include_router(router)
