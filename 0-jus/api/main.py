"""
api/main.py
-----------
API REST para previsao de chances de procedencia de processos judiciais.

Executar:
  uvicorn api.main:app --reload --port 8000

Endpoints:
  POST /prever       — previsao completa com SHAP
  GET  /tribunais    — lista de tribunais disponiveis
  GET  /temas        — lista de temas (assuntos) disponiveis
  GET  /health       — status da API
"""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from jurimetria.predicao import prever, ENCODERS, META

app = FastAPI(
    title="Jurimetria API",
    description="Previsao de chances de procedencia de processos judiciais via XGBoost + SHAP",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CasoInput(BaseModel):
    tribunal: str = Field(..., example="TJSP", description="Sigla do tribunal (ex: TJSP, TJRJ)")
    tema: str = Field(..., example="10433", description="Codigo do assunto (TPU/CNJ)")
    taxa_vitoria_juiz: float = Field(0.55, ge=0.0, le=1.0, description="Taxa historica de procedencia do orgao julgador")
    taxa_vitoria_tribunal: float = Field(0.55, ge=0.0, le=1.0, description="Taxa historica de procedencia do tribunal")
    taxa_vitoria_tema: float = Field(0.55, ge=0.0, le=1.0, description="Taxa historica de procedencia do assunto")
    prec_favoraveis: int = Field(0, ge=0, description="Numero de movimentos/precedentes favoraveis")
    qualidade_provas: int = Field(1, ge=0, le=2, description="Qualidade das provas: 0=fraca, 1=media, 2=forte")
    segundo_grau: int = Field(0, ge=0, le=1, description="Instancia: 0=primeira, 1=segunda")


class ContribuicaoSHAP(BaseModel):
    feature: str
    valor: float
    direcao: str


class PrevisaoOutput(BaseModel):
    probabilidade_pct: float
    intervalo_confianca: float
    resumo: str
    faixa: str
    cor: str
    n_casos_base: int
    contribuicoes_shap: dict[str, float]
    modelo_auc: float
    modelo_versao: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "modelo_auc": META["auc_cv_medio"],
        "n_treino": META["n_treino"],
        "versao": META["versao"],
    }


@app.get("/tribunais")
def listar_tribunais():
    return {"tribunais": sorted(ENCODERS["tribunal"].keys())}


@app.get("/temas")
def listar_temas():
    return {"temas": sorted(ENCODERS["tema"].keys())}


@app.post("/prever", response_model=PrevisaoOutput)
def endpoint_prever(caso: CasoInput):
    if caso.tribunal not in ENCODERS["tribunal"]:
        raise HTTPException(
            status_code=422,
            detail=f"Tribunal '{caso.tribunal}' nao reconhecido. Use GET /tribunais para ver os disponiveis.",
        )

    resultado = prever(caso.model_dump())

    return PrevisaoOutput(
        **resultado,
        modelo_auc=META["auc_cv_medio"],
        modelo_versao=META["versao"],
    )
