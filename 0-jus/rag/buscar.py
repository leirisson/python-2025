"""
rag/buscar.py
-------------
Motor de busca de jurisprudência.
Funciona com TF-IDF (local, sem internet) ou OpenAI/BERT.
"""
import os, sqlite3, json
from pathlib import Path
from typing import Optional

DB_DIR      = Path("data/rag")
SQLITE_PATH = DB_DIR / "jurisprudencia.db"

_docs_cache: dict = {}   # id -> metadata + ementa

def _carregar_docs():
    global _docs_cache
    if _docs_cache:
        return
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM decisoes").fetchall()
    for r in rows:
        _docs_cache[r["id"]] = dict(r)
    conn.close()

def buscar_precedentes(
    texto_consulta: str,
    n_resultados: int = 5,
    tribunal: Optional[str] = None,
    segmento: Optional[str] = None,
    apenas_procedentes: bool = False,
) -> list[dict]:
    from rag.embedding import tfidf_buscar, embedder_disponivel, TFIDF_PATH
    if not TFIDF_PATH.exists():
        raise FileNotFoundError(
            "Base RAG não encontrada. Execute: python rag/1_indexar.py"
        )
    _carregar_docs()
    pares = tfidf_buscar(texto_consulta, n_resultados * 3)

    resultados = []
    for doc_id, score in pares:
        doc = _docs_cache.get(doc_id)
        if not doc:
            continue
        if tribunal and doc.get("tribunal") != tribunal:
            continue
        if segmento and doc.get("segmento") != segmento:
            continue
        if apenas_procedentes and doc.get("label") != 1:
            continue
        resultados.append({
            "tribunal":     doc.get("tribunal", ""),
            "segmento":     doc.get("segmento", ""),
            "assunto":      doc.get("assunto_nome", ""),
            "resultado":    "Procedente" if doc.get("label") == 1 else "Improcedente",
            "grau":         doc.get("grau", ""),
            "ementa":       doc.get("ementa", ""),
            "similaridade": round(score * 100, 1),
        })
        if len(resultados) >= n_resultados:
            break

    return resultados

def formatar_para_prompt(precedentes: list[dict]) -> str:
    if not precedentes:
        return "Nenhum precedente relevante encontrado."
    linhas = ["JURISPRUDÊNCIA RELEVANTE:\n"]
    for i, p in enumerate(precedentes, 1):
        linhas.append(
            f"[{i}] {p['tribunal']} — {p['assunto']}\n"
            f"    Resultado: {p['resultado']} | Similaridade: {p['similaridade']}%\n"
            f"    {p['ementa']}\n"
        )
    return "\n".join(linhas)

def estatisticas_base() -> dict:
    conn = sqlite3.connect(SQLITE_PATH)
    total = conn.execute("SELECT COUNT(*) FROM decisoes").fetchone()[0]
    por_tribunal = dict(conn.execute(
        "SELECT tribunal, COUNT(*) FROM decisoes GROUP BY tribunal ORDER BY 2 DESC LIMIT 10"
    ).fetchall())
    por_segmento = dict(conn.execute(
        "SELECT segmento, COUNT(*) FROM decisoes GROUP BY segmento"
    ).fetchall())
    taxa = conn.execute("SELECT ROUND(AVG(label)*100,1) FROM decisoes").fetchone()[0]
    conn.close()
    return {"total_decisoes": total, "por_tribunal": por_tribunal,
            "por_segmento": por_segmento, "taxa_procedencia": taxa}
