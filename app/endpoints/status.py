from fastapi import APIRouter
from app.models import StatusResponse

router = APIRouter()

@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Verifica o status da API",
    tags=["Status"]
)
async def get_status():
    """Endpoint simples para verificar se a API está online."""
    return {"status": "ok"}