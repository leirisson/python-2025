"""
jurimetria/simulado/gerar_dados.py
-----------------------------------
Gera um dataset simulado de processos judiciais brasileiros.
Na produção, use o fluxo coleta/ para dados reais do DataJud.
"""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "data"

SEED = 42

TRIBUNAIS = {
    "TJSP": 0.55, "TJRJ": 0.52, "TJMG": 0.54,
    "TRT2": 0.61, "TRT3": 0.59, "TRF3": 0.67, "TRF4": 0.65,
}

TEMAS = {
    "Dano moral consumidor":      0.65,
    "Horas extras trabalhista":   0.62,
    "Aposentadoria especial":     0.70,
    "Rescisão indireta":          0.58,
    "Cobrança indevida":          0.68,
    "Acidente de trabalho":       0.60,
    "Revisão de benefício INSS":  0.66,
    "Indenização cível":          0.45,
    "Despejo por falta de pgto":  0.40,
    "Busca e apreensão":          0.38,
}

RESULTADOS_TEXTO = {
    1: [
        "Julgo PROCEDENTE o pedido e condeno o réu ao pagamento.",
        "DEFIRO o pedido. Condeno ao pagamento de danos morais.",
        "Dou PROVIMENTO ao recurso. Procedente o pleito autoral.",
        "ACOLHO os pedidos formulados na inicial.",
    ],
    0: [
        "Julgo IMPROCEDENTE o pedido. Sem custas.",
        "INDEFIRO o pedido por ausência de prova.",
        "NEGO PROVIMENTO ao recurso. Improcedente.",
        "REJEITO os pedidos. Extinção com resolução do mérito.",
    ],
}


def gerar(n: int = 10_000) -> pd.DataFrame:
    np.random.seed(SEED)

    tribunais = np.random.choice(list(TRIBUNAIS.keys()), n)
    temas     = np.random.choice(list(TEMAS.keys()), n)
    valores   = np.random.lognormal(mean=10.5, sigma=1.2, size=n).astype(int)
    graus     = np.random.choice([1, 2], n, p=[0.70, 0.30])

    n_juizes  = 200
    juiz_ids  = np.random.randint(0, n_juizes, n)
    juiz_taxa = {j: np.clip(np.random.normal(0.55, 0.12), 0.15, 0.90) for j in range(n_juizes)}
    taxa_juiz = np.array([juiz_taxa[j] for j in juiz_ids])

    prec_favoraveis  = np.random.poisson(lam=15, size=n)
    qualidade_provas = np.random.choice([0, 1, 2], n, p=[0.25, 0.45, 0.30])

    prob_base = (
        np.array([TRIBUNAIS[t] for t in tribunais]) * 0.20 +
        np.array([TEMAS[t]     for t in temas])     * 0.30 +
        taxa_juiz                                   * 0.25 +
        (qualidade_provas / 2)                      * 0.15 +
        np.clip(prec_favoraveis / 50, 0, 1)         * 0.10
    )
    prob_base = np.clip(prob_base, 0.05, 0.95)
    labels = (np.random.rand(n) < prob_base).astype(int)

    ementas = [
        np.random.choice(RESULTADOS_TEXTO[lbl]) + f" Processo nº {i:07d}."
        for i, lbl in enumerate(labels)
    ]

    df = pd.DataFrame({
        "numero_processo":   [f"{i:07d}-{np.random.randint(10, 99)}.2023.8.26.0100" for i in range(n)],
        "tribunal":          tribunais,
        "tema":              temas,
        "valor_causa":       valores,
        "grau":              graus,
        "juiz_id":           juiz_ids,
        "taxa_vitoria_juiz": taxa_juiz.round(4),
        "prec_favoraveis":   prec_favoraveis,
        "qualidade_provas":  qualidade_provas,
        "prob_real":         prob_base.round(4),
        "ementa":            ementas,
        "label":             labels,
    })

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_DIR / "processos_raw.csv", index=False)

    print(f"✅  Dataset gerado: {len(df):,} processos")
    print(f"    Procedentes   : {labels.sum():,} ({labels.mean()*100:.1f}%)")
    print(f"    Improcedentes : {(1-labels).sum():,} ({(1-labels.mean())*100:.1f}%)")
    print(f"    Arquivo       : {DATA_DIR / 'processos_raw.csv'}")

    return df


if __name__ == "__main__":
    gerar()
