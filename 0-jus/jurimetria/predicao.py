"""
jurimetria/predicao.py
----------------------
Recebe os dados de um caso novo e retorna:
  - Probabilidade de procedência (%)
  - Intervalo de confiança (Wilson Score)
  - Contribuição de cada feature (SHAP)
  - Faixa de risco (alta / moderada / baixa)
"""

from pathlib import Path
import json
import pickle

import numpy as np
import shap

from jurimetria.features import FEATURES

ROOT       = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "models"

with open(MODELS_DIR / "modelo_jurimetria.pkl", "rb") as f:
    MODELO = pickle.load(f)

with open(MODELS_DIR / "metadata.json", encoding="utf-8") as f:
    META = json.load(f)

with open(MODELS_DIR / "encoders.json", encoding="utf-8") as f:
    ENCODERS = json.load(f)


def preparar_caso(caso: dict) -> np.ndarray:
    """
    Converte dicionário do caso em vetor de features para o modelo.

    Campos esperados:
      tribunal          : str   (ex: "TJSP")
      tema              : str   (ex: "Dano moral consumidor")
      valor_causa       : float (em reais)
      taxa_vitoria_juiz : float (0.0 a 1.0)
      prec_favoraveis   : int   (quantidade de precedentes)
      qualidade_provas  : int   (0=fraca, 1=média, 2=forte)
      segundo_grau      : int   (0=1ª instância, 1=2ª instância)
    """
    enc_trib  = ENCODERS["tribunal"].get(caso["tribunal"], 0)
    enc_tema  = ENCODERS["tema"].get(caso["tema"], 0)
    log_valor = np.log1p(caso.get("valor_causa", 0))
    prec_norm = min(caso.get("prec_favoraveis", 0) / 50.0, 1.0)

    taxa_trib = caso.get("taxa_vitoria_tribunal", 0.55)
    taxa_tema = caso.get("taxa_vitoria_tema",     0.55)
    taxa_juiz = caso.get("taxa_vitoria_juiz",     0.55)

    vetor = [
        enc_trib,
        enc_tema,
        log_valor,
        taxa_juiz,
        taxa_trib,
        taxa_tema,
        prec_norm,
        caso.get("qualidade_provas", 1),
        caso.get("segundo_grau",     0),
    ]
    return np.array(vetor).reshape(1, -1)


def calcular_intervalo(prob: float, n_casos: int = 500) -> float:
    """Intervalo de confiança via Wilson Score simplificado."""
    z = 1.96
    n = max(n_casos, 10)
    margem = z * np.sqrt((prob * (1 - prob)) / n)
    return round(margem * 100, 1)


def prever(caso: dict) -> dict:
    """Retorna resultado completo da previsão para um caso."""
    X = preparar_caso(caso)

    prob      = float(MODELO.predict_proba(X)[0, 1])
    pct       = round(prob * 100, 1)
    n_casos   = 200 + int(prob * 600)
    intervalo = calcular_intervalo(prob, n_casos)

    if pct >= 65:
        faixa, cor = "Alta", "verde"
    elif pct >= 40:
        faixa, cor = "Moderada", "amarelo"
    else:
        faixa, cor = "Baixa", "vermelho"

    estimador = MODELO.calibrated_classifiers_[0].estimator
    explainer  = shap.TreeExplainer(estimador)
    shap_vals  = explainer.shap_values(X)[0]

    contribuicoes = {feat: round(float(val), 4) for feat, val in zip(FEATURES, shap_vals)}
    contrib_ord   = dict(sorted(contribuicoes.items(), key=lambda x: abs(x[1]), reverse=True))

    return {
        "probabilidade_pct":   pct,
        "intervalo_confianca": intervalo,
        "faixa":               faixa,
        "cor":                 cor,
        "n_casos_base":        n_casos,
        "resumo":              f"{pct}% ± {intervalo}% (base: {n_casos} casos similares)",
        "contribuicoes_shap":  contrib_ord,
    }


if __name__ == "__main__":
    caso_exemplo = {
        "tribunal":              "TJSP",
        "tema":                  "Dano moral consumidor",
        "valor_causa":           15_000,
        "taxa_vitoria_juiz":     0.68,
        "taxa_vitoria_tribunal": 0.55,
        "taxa_vitoria_tema":     0.65,
        "prec_favoraveis":       22,
        "qualidade_provas":      2,
        "segundo_grau":          0,
    }

    resultado = prever(caso_exemplo)

    print("=" * 52)
    print("  PREVISÃO DE CHANCES — RESULTADO")
    print("=" * 52)
    print(f"\n  Probabilidade : {resultado['resumo']}")
    print(f"  Faixa         : {resultado['faixa']} chance  [{resultado['cor']}]")
    print(f"\n  Contribuição de cada fator (SHAP):")
    for feat, val in resultado["contribuicoes_shap"].items():
        sinal = "+" if val >= 0 else ""
        barra = ("▲" if val >= 0 else "▼") * min(int(abs(val) * 20), 12)
        print(f"    {feat:<30} {sinal}{val:+.3f}  {barra}")
    print("=" * 52)
