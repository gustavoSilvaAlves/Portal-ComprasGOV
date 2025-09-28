import asyncio
from fastapi import APIRouter, HTTPException, status
from app.models import HCaptchaResponse, ErrorResponse
from app.core import CONCURRENCY_LIMITER, logger
from app.services import solve_hcaptcha_sync

router = APIRouter()

@router.get(
    "/get_hcaptcha",
    response_model=HCaptchaResponse,
    summary="Obtém um token hCaptcha",
    tags=["Captcha"],
    responses={
        500: {"model": ErrorResponse, "description": "Falha ao obter o token"},
        503: {"model": ErrorResponse, "description": "Serviço indisponível (muitas requisições)"}
    }
)
async def get_hcaptcha_token():
    """
    Inicia o processo para resolver o hCaptcha.
    Esta operação é intensiva e as requisições serão enfileiradas.
    """
    logger.info("Requisição para /get_hcaptcha recebida. Aguardando slot de execução...")
    try:
        async with asyncio.timeout(90):
            async with CONCURRENCY_LIMITER:
                logger.info("Slot adquirido. Iniciando processo em thread...")
                token = await asyncio.to_thread(solve_hcaptcha_sync)
                if not token:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Não foi possível capturar o hCaptcha."
                    )
                logger.info("Processo finalizado e slot liberado.")
                return HCaptchaResponse(hcaptcha_token=token)
    except TimeoutError:
        logger.warning("A requisição excedeu o timeout.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço sobrecarregado. Tente novamente."
        )
    except Exception as e:
        logger.error(f"Erro não tratado: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno inesperado."
        )