"""
jurimetria/coleta/consolidar.py
---------------------------------
Lê todos os CSVs em data/raw/, consolida em um único dataset,
calcula taxas históricas e entrega features.csv pronto para treino.

Execute:  python -m jurimetria.coleta.consolidar
"""

from pathlib import Path
import pandas as pd
import numpy as np

from jurimetria.features import (
    FEATURES,
    adicionar_taxas_vitoria,
    encodar_categoricos,
    salvar_encoders,
    selecionar_features,
)

ROOT      = Path(__file__).resolve().parent.parent.parent
RAW_DIR   = ROOT / "data" / "raw"
DATA_DIR  = ROOT / "data"
MODEL_DIR = ROOT / "models"


def consolidar() -> pd.DataFrame:
    # ── 1. Carrega e empilha CSVs ────────────────────────────────────
    arquivos = list(RAW_DIR.glob("*.csv"))
    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo em {RAW_DIR}.\n"
            "Execute primeiro: python -m jurimetria.coleta.coletar_datajud"
        )

    partes = []
    for arq in arquivos:
        df_arq = pd.read_csv(arq)
        partes.append(df_arq)
        print(f"  Lido: {arq.name} — {len(df_arq):,} processos")

    df = pd.concat(partes, ignore_index=True)
    print(f"\n  Total bruto: {len(df):,} processos")

    # ── 2. Limpeza ───────────────────────────────────────────────────
    df = df.dropna(subset=["label", "tribunal", "assunto_codigo"])
    df = df.drop_duplicates(subset=["numero_processo"])
    df["label"]      = df["label"].astype(int)
    df["valor_causa"] = pd.to_numeric(df["valor_causa"], errors="coerce").fillna(0)
    df["grau_num"]   = df["grau"].str.extract(r"(\d)").fillna("1").astype(int).clip(1, 2)

    print(f"  Após limpeza: {len(df):,} processos")
    print(f"  Procedentes : {df['label'].sum():,} ({df['label'].mean()*100:.1f}%)")

    # ── 3. Features via módulo compartilhado ─────────────────────────
    df = adicionar_taxas_vitoria(
        df,
        col_tribunal="tribunal",
        col_tema="assunto_codigo",
        col_juiz="orgao_julgador",
    )

    df, mapeamento = encodar_categoricos(df, col_tribunal="tribunal", col_tema="assunto_codigo")

    df["segundo_grau"]    = (df["grau_num"] == 2).astype(int)
    df["prec_norm"]       = np.clip(df["n_movimentos"] / 30.0, 0, 1)
    df["qualidade_provas"] = 1  # não disponível na API; advogado informa na inferência

    # ── 4. Salva encoders e dataset final ───────────────────────────
    salvar_encoders(mapeamento, MODEL_DIR / "encoders.json")

    df_final = selecionar_features(df).dropna()
    df_final.to_csv(DATA_DIR / "features.csv", index=False)

    print(f"\n  Distribuição por tribunal:")
    resumo = df.groupby("tribunal")["label"].agg(["count", "mean"])
    resumo.columns = ["processos", "taxa_proc"]
    print(resumo.to_string())

    print(f"\n  Dataset final: {len(df_final):,} processos")
    print(f"  Arquivo: {DATA_DIR / 'features.csv'}")
    print("  Proximo: python -m jurimetria.modelo")

    return df_final


if __name__ == "__main__":
    consolidar()
