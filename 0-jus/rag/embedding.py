"""
rag/embedding.py
----------------
Camada de embedding com 3 opções, da mais simples à melhor:

  MODO_TFIDF    → TF-IDF local (sklearn). Funciona offline, sem GPU.
                  Boa para começar, ruim para sinônimos.

  MODO_OPENAI   → text-embedding-3-small via API OpenAI.
                  Melhor qualidade, ~$0.02/1M tokens. Precisa de chave.

  MODO_BERT     → BERTimbau (neuralmind/bert-base-portuguese-cased).
                  Melhor para PT-BR jurídico. Precisa de GPU ou paciência.
                  pip install sentence-transformers

Configure EMBEDDING_MODE abaixo ou via variável de ambiente:
  export EMBEDDING_MODE=openai
  export OPENAI_API_KEY=sk-...
"""

import os
import pickle
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

EMBEDDING_MODE = os.getenv("EMBEDDING_MODE", "tfidf")  # tfidf | openai | bert

DB_DIR = Path("data/rag")
DB_DIR.mkdir(parents=True, exist_ok=True)
TFIDF_PATH = DB_DIR / "tfidf_model.pkl"
TFIDF_VECS_PATH = DB_DIR / "tfidf_vectors.pkl"


# ── TF-IDF (modo local, sem dependências externas) ───────────────────

_tfidf_model    = None
_tfidf_vectors  = None
_tfidf_docs_ids = None


def tfidf_fit(textos: list[str], ids: list[str]):
    global _tfidf_model, _tfidf_vectors, _tfidf_docs_ids
    _tfidf_model = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        max_features=50_000,
        sublinear_tf=True,
    )
    _tfidf_vectors  = _tfidf_model.fit_transform(textos)
    _tfidf_docs_ids = ids
    with open(TFIDF_PATH, "wb") as f:
        pickle.dump(_tfidf_model, f)
    with open(TFIDF_VECS_PATH, "wb") as f:
        pickle.dump((_tfidf_vectors, _tfidf_docs_ids), f)
    print(f"  TF-IDF: {len(textos)} documentos indexados, vocab={_tfidf_model.vocabulary_.__len__()}")


def tfidf_load():
    global _tfidf_model, _tfidf_vectors, _tfidf_docs_ids
    if _tfidf_model is not None:
        return
    with open(TFIDF_PATH, "rb") as f:
        _tfidf_model = pickle.load(f)
    with open(TFIDF_VECS_PATH, "rb") as f:
        _tfidf_vectors, _tfidf_docs_ids = pickle.load(f)


def tfidf_buscar(query: str, n: int = 5) -> list[tuple[str, float]]:
    tfidf_load()
    vec = _tfidf_model.transform([query])
    sims = cosine_similarity(vec, _tfidf_vectors).flatten()
    top_idx = sims.argsort()[::-1][:n]
    return [(_tfidf_docs_ids[i], float(sims[i])) for i in top_idx if sims[i] > 0]


# ── OpenAI Embeddings ────────────────────────────────────────────────

def openai_embed(textos: list[str]) -> list[list[float]]:
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("pip install openai")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.embeddings.create(
        input=textos,
        model="text-embedding-3-small",
    )
    return [r.embedding for r in resp.data]


# ── BERTimbau ────────────────────────────────────────────────────────

def bert_embed(textos: list[str]) -> list[list[float]]:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError("pip install sentence-transformers")
    model = SentenceTransformer("neuralmind/bert-base-portuguese-cased")
    return model.encode(textos, show_progress_bar=True).tolist()


# ── Interface unificada ──────────────────────────────────────────────

def embedder_disponivel() -> str:
    """Retorna qual modo de embedding está configurado e disponível."""
    if EMBEDDING_MODE == "openai" and os.getenv("OPENAI_API_KEY"):
        return "openai"
    if EMBEDDING_MODE == "bert":
        try:
            import sentence_transformers
            return "bert"
        except ImportError:
            pass
    return "tfidf"
