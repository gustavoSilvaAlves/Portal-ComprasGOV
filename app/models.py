from pydantic import BaseModel, Field

class StatusResponse(BaseModel):
    status: str = Field(..., example="ok", description="Status da API")

class HCaptchaResponse(BaseModel):
    hcaptcha_token: str = Field(..., example="P1_eyJ...U5Z", description="Token hCaptcha resolvido")

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Não foi possível capturar o hCaptcha.")

class PropostasRequest(BaseModel):
    id_compra: str = Field(..., example="15815405902172025", description="ID da Compra (ou pregão)")
    id_item: str = Field(..., example="1", description="ID do Item dentro da compra")
    token: str = Field(..., alias="hcaptcha_token", description="Token hCaptcha obtido no endpoint anterior")

class AcompanhamentoRequest(BaseModel):
    """Modelo para a requisição de acompanhamento da contratação."""
    id_compra: str = Field(..., description="ID da compra (UASG + Número do Pregão). Ex: 99999905000012024")
    token: str = Field(..., description="Token hCaptcha obtido.")