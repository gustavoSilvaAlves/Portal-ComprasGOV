from typing import Any
import httpx
from fastapi import APIRouter, HTTPException, status
from app.models import PropostasRequest, ErrorResponse
from app.core import logger

router = APIRouter()

@router.post(
    "/get_propostas",
    response_model=Any,
    summary="Obtém as propostas de um item",
    tags=["Consultas ComprasGOV"],
    responses={
        404: {"model": ErrorResponse, "description": "Compra ou item não encontrado"},
        500: {"model": ErrorResponse, "description": "Erro na API externa"}
    }
)
async def get_propostas(request_data: PropostasRequest):
    """
    Busca as propostas de um item específico, utilizando o token hCaptcha.

    - **id_compra**: ID da compra (UASG + Número do Pregão). Ex: 99999905000012024
    - **id_item**: ID do item específico dentro da compra. Ex: 1
    - **token**: Token hCaptcha válido obtido anteriormente.
    """
    base_url = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/public/v1/compras"
    target_url = (
        f"{base_url}/{request_data.id_compra}/itens/{request_data.id_item}/propostas"
        f"?captcha={request_data.token}"
    )
    logger.info(f"Fazendo requisição para: {target_url}")
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(target_url, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro de status da API externa: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="Erro na API do ComprasNet.")
    except httpx.RequestError as e:
        logger.error(f"Erro de rede ao contatar a API externa: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Não foi possível conectar ao ComprasNet.")