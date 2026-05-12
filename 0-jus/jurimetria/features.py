"""
jurimetria/features.py
----------------------
Transformações de features compartilhadas entre o fluxo simulado
(simulado/gerar_dados.py) e o fluxo real (coleta/consolidar.py).
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd

FEATURES = [
    "tribunal_enc",
    "tema_enc",
    "taxa_vitoria_juiz",
    "taxa_vitoria_tribunal",
    "taxa_vitoria_tema",
    "prec_norm",
    "qualidade_provas",
    "segundo_grau",
]


def adicionar_log_valor(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica log1p ao valor da causa para reduzir assimetria da distribuição."""
    df = df.copy()
    df["log_valor"] = np.log1p(df["valor_causa"])
    return df


def adicionar_taxas_vitoria(
    df: pd.DataFrame,
    col_tribunal: str,
    col_tema: str,
    col_juiz: str | None,
    col_label: str = "label",
) -> pd.DataFrame:
    """
    Calcula taxas históricas de vitória por tribunal, tema e juiz.

    col_juiz: coluna com o juiz/órgão julgador. Se None, usa a taxa do tribunal
              como fallback (caso em que a taxa já vem no df — fluxo simulado).
    """
    df = df.copy()

    taxa_trib = df.groupby(col_tribunal)[col_label].mean().rename("taxa_vitoria_tribunal")
    df = df.merge(taxa_trib, on=col_tribunal, how="left")

    taxa_tema = df.groupby(col_tema)[col_label].mean().rename("taxa_vitoria_tema")
    df = df.merge(taxa_tema, on=col_tema, how="left")

    if col_juiz is not None:
        taxa_juiz = df.groupby(col_juiz)[col_label].mean().rename("taxa_vitoria_juiz")
        df = df.merge(taxa_juiz, on=col_juiz, how="left")
        df["taxa_vitoria_juiz"] = df["taxa_vitoria_juiz"].fillna(df["taxa_vitoria_tribunal"])

    return df


def encodar_categoricos(
    df: pd.DataFrame, col_tribunal: str, col_tema: str
) -> tuple[pd.DataFrame, dict]:
    """
    Codifica tribunal e tema como inteiros usando pd.Categorical.
    Retorna o df atualizado e o dicionário de mapeamento para salvar.
    """
    df = df.copy()
    trib_cat = pd.Categorical(df[col_tribunal])
    tema_cat = pd.Categorical(df[col_tema])
    df["tribunal_enc"] = trib_cat.codes
    df["tema_enc"] = tema_cat.codes

    n_trib = range(len(trib_cat.categories))
    n_tema = range(len(tema_cat.categories))
    mapeamento = {
        "tribunal": {str(k): int(v) for k, v in zip(trib_cat.categories, n_trib)},
        "tema":     {str(k): int(v) for k, v in zip(tema_cat.categories, n_tema)},
    }
    return df, mapeamento


def salvar_encoders(mapeamento: dict, path: Path) -> None:
    """Persiste o dicionário de mapeamento categórico em JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mapeamento, f, ensure_ascii=False, indent=2)


def selecionar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna apenas as colunas de features, label e número do processo."""
    return df[FEATURES + ["label", "numero_processo"]].copy()


def processar_simulado(df: pd.DataFrame, models_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    """
    Pipeline completo de features para o fluxo simulado.
    Os dados já contêm taxa_vitoria_juiz calculada na geração.
    """
    df = adicionar_log_valor(df)
    df = adicionar_taxas_vitoria(df, col_tribunal="tribunal", col_tema="tema", col_juiz=None)
    df, mapeamento = encodar_categoricos(df, col_tribunal="tribunal", col_tema="tema")
    salvar_encoders(mapeamento, models_dir / "encoders.json")

    df["segundo_grau"] = (df["grau"] == 2).astype(int)
    df["prec_norm"]    = np.clip(df["prec_favoraveis"] / 50.0, 0, 1)

    df_out = selecionar_features(df)
    return df_out, FEATURES
