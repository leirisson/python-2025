"""
scripts/pipeline_real.py
--------------------------
Pipeline com dados reais do DataJud:
  1. Consolida os CSVs coletados em data/raw/
  2. Treina e calibra o modelo XGBoost
  3. Testa uma previsão de exemplo

Pré-requisito: executar coleta antes
  python -m jurimetria.coleta.testar_conexao
  python -m jurimetria.coleta.coletar_datajud

Execute:  python scripts/pipeline_real.py
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jurimetria.coleta.consolidar import consolidar
from jurimetria.modelo import treinar
from jurimetria.predicao import prever


def titulo(txt: str) -> None:
    print(f"\n{'─'*54}")
    print(f"  {txt}")
    print(f"{'─'*54}")


if __name__ == "__main__":
    titulo("PASSO 1 — Consolidando dados coletados")
    consolidar()

    titulo("PASSO 2 — Treinando o modelo XGBoost")
    modelo, metadata = treinar()

    titulo("PASSO 3 — Testando previsão num caso real")
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
    print(f"  AUC-ROC : {metadata['auc_cv_medio']:.4f} ± {metadata['auc_cv_std']:.4f}")
    print(f"  Brier   : {metadata['brier_score']:.4f}")
