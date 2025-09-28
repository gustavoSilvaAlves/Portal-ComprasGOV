from fastapi import FastAPI
from app.core import settings
from app.endpoints import status, token, propostas, acompanhamento


app = FastAPI(
    title=settings.app_name,
    description="API para consulta das endpoints do ComprasGov.",
    version="1.0.0"
)

app.include_router(status.router, prefix="/api/v1")


app.include_router(token.router, prefix="/api/v1")


app.include_router(propostas.router, prefix="/api/v1")

app.include_router(acompanhamento.router, prefix="/api/v1")