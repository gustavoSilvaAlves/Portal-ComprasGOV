from typing import Any
import httpx
from fastapi import APIRouter, HTTPException, status
from app.models import AcompanhamentoRequest, ErrorResponse
from app.core import logger

router = APIRouter()

@router.post(
    "/get_acompanhamento",
    response_model=Any,
    summary="Obtém o acompanhamento de uma contratação",
    tags=["Consultas ComprasGOV"],
    responses={
        404: {"model": ErrorResponse, "description": "Compra não encontrada"},
        500: {"model": ErrorResponse, "description": "Erro na API externa"}
    }
)
async def get_acompanhamento(request_data: AcompanhamentoRequest):
    """
    Busca os detalhes de acompanhamento de uma compra específica, utilizando o token hCaptcha.

    - **id_compra**: ID da compra (UASG + Número do Pregão). Ex: 99999905000012024
    - **token**: Token hCaptcha válido obtido anteriormente.
    """
    base_url = "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-fase-externa/public/v1/compras"
    # A URL alvo é montada com o id_compra e o token (captcha)
    target_url = f"{base_url}/{request_data.id_compra}?captcha={request_data.token}"

    logger.info(f"Fazendo requisição para: {target_url}")
    try:
        # Usamos httpx para fazer a requisição GET assíncrona
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(target_url, timeout=30.0)
            response.raise_for_status()  # Lança uma exceção para status de erro (4xx ou 5xx)
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro de status da API externa: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Erro na API do ComprasNet. Verifique se o ID da compra está correto."
        )
    except httpx.RequestError as e:
        logger.error(f"Erro de rede ao contatar a API externa: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível conectar ao ComprasNet."
        )
