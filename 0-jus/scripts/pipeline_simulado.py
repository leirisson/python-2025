"""
scripts/pipeline_simulado.py
-----------------------------
Pipeline completo com dados simulados:
  1. Gera dataset sintético
  2. Calcula features
  3. Treina e calibra o modelo XGBoost
  4. Testa uma previsão de exemplo

Execute:  python scripts/pipeline_simulado.py
"""

from pathlib import Path
import sys

# Garante que a raiz do projeto está no path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from jurimetria.simulado.gerar_dados import gerar
from jurimetria.features import processar_simulado
from jurimetria.modelo import treinar
from jurimetria.predicao import prever

DATA_DIR   = ROOT / "data"
MODELS_DIR = ROOT / "models"


def titulo(txt: str) -> None:
    print(f"\n{'─'*54}")
    print(f"  {txt}")
    print(f"{'─'*54}")


if __name__ == "__main__":
    titulo("PASSO 1 — Gerando dados simulados")
    df_raw = gerar()

    titulo("PASSO 2 — Feature engineering")
    DATA_DIR.mkdir(exist_ok=True)
    df_feat, features = processar_simulado(df_raw, MODELS_DIR)
    df_feat.to_csv(DATA_DIR / "features.csv", index=False)
    print(f"✅  Features: {df_feat.shape[0]:,} linhas × {len(features)} colunas")
    print(f"    Arquivo : {DATA_DIR / 'features.csv'}")

    titulo("PASSO 3 — Treinando o modelo XGBoost")
    modelo, metadata = treinar()

    titulo("PASSO 4 — Testando previsão num caso real")
    caso_teste = {
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
    resultado = prever(caso_teste)

    print(f"\n  Probabilidade : {resultado['resumo']}")
    print(f"  Faixa         : {resultado['faixa']} chance  [{resultado['cor']}]")
    print(f"\n  Top 3 fatores que mais pesaram:")
    for i, (feat, val) in enumerate(list(resultado["contribuicoes_shap"].items())[:3]):
        sinal = "aumenta" if val >= 0 else "reduz"
        print(f"    {i+1}. {feat} → {sinal} a chance ({val:+.3f})")

    titulo("PIPELINE CONCLUÍDO")
    print(f"  Modelo  : {MODELS_DIR / 'modelo_jurimetria.pkl'}")
    print(f"  AUC-ROC : {metadata['auc_cv_medio']:.4f} ± {metadata['auc_cv_std']:.4f}")
    print(f"  Brier   : {metadata['brier_score']:.4f}")
    print(f"\n  Próximos passos:")
    print(f"    → Coletar dados reais: python -m jurimetria.coleta.coletar_datajud")
    print(f"    → Pipeline real      : python scripts/pipeline_real.py")
