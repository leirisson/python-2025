"""
jurimetria/modelo.py
--------------------
Treina o modelo XGBoost com validação cruzada estratificada,
calibra as probabilidades e salva o modelo final.
"""

from pathlib import Path
import json
import pickle

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, classification_report, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from xgboost import XGBClassifier

from jurimetria.features import FEATURES

ROOT       = Path(__file__).resolve().parent.parent
DATA_DIR   = ROOT / "data"
MODELS_DIR = ROOT / "models"

SEED = 42


def treinar() -> tuple:
    df = pd.read_csv(DATA_DIR / "features.csv")
    X  = df[FEATURES].values
    y  = df["label"].values

    print(f"Dataset: {len(df):,} processos | procedentes: {y.mean()*100:.1f}%\n")

    neg, pos = (y == 0).sum(), (y == 1).sum()
    spw = neg / pos

    modelo_base = XGBClassifier(
        n_estimators     =200,
        max_depth        =4,
        learning_rate    =0.05,
        subsample        =0.8,
        colsample_bytree =0.8,
        scale_pos_weight =spw,
        random_state     =SEED,
        eval_metric      ="auc",
        verbosity        =0,
        use_label_encoder=False,
    )

    print("Validacao cruzada (5 folds)...")
    cv     = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    aucs   = cross_val_score(modelo_base, X, y, cv=cv, scoring="roc_auc")
    briers = cross_val_score(modelo_base, X, y, cv=cv, scoring="neg_brier_score")

    print(f"    AUC-ROC medio : {aucs.mean():.4f} +/- {aucs.std():.4f}")
    print(f"    Brier score   : {(-briers.mean()):.4f} +/- {briers.std():.4f}\n")

    print("Calibrando probabilidades (Isotonic Regression)...")
    modelo_calibrado = CalibratedClassifierCV(modelo_base, method="isotonic", cv=5)
    modelo_calibrado.fit(X, y)

    probs      = modelo_calibrado.predict_proba(X)[:, 1]
    preds      = (probs >= 0.5).astype(int)
    auc_final  = roc_auc_score(y, probs)
    brier_final = brier_score_loss(y, probs)

    print(f"\nMetricas finais (conjunto completo):")
    print(f"    AUC-ROC     : {auc_final:.4f}")
    print(f"    Brier score : {brier_final:.4f}  (0 = perfeito, 0.25 = chute)\n")
    print("    Relatorio de classificacao:")
    print(classification_report(y, preds, target_names=["Improcedente", "Procedente"]))

    estimador_base = modelo_calibrado.calibrated_classifiers_[0].estimator
    importancias   = dict(zip(FEATURES, estimador_base.feature_importances_))
    importancias   = dict(sorted(importancias.items(), key=lambda x: x[1], reverse=True))

    print("    Importancia das features:")
    for feat, imp in importancias.items():
        barra = "#" * int(imp * 40)
        print(f"      {feat:<30} {barra} {imp:.4f}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    with open(MODELS_DIR / "modelo_jurimetria.pkl", "wb") as f:
        pickle.dump(modelo_calibrado, f)

    metadata = {
        "features":     FEATURES,
        "n_treino":     int(len(df)),
        "auc_cv_medio": round(float(aucs.mean()), 4),
        "auc_cv_std":   round(float(aucs.std()),  4),
        "brier_score":  round(float(brier_final), 4),
        "importancias": {k: round(float(v), 4) for k, v in importancias.items()},
        "threshold":    0.5,
        "versao":       "1.0.0",
    }
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\nModelo salvo em {MODELS_DIR / 'modelo_jurimetria.pkl'}")
    print(f"Metadados   em {MODELS_DIR / 'metadata.json'}")

    return modelo_calibrado, metadata


if __name__ == "__main__":
    treinar()
