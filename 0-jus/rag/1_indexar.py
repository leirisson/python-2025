"""
rag/1_indexar.py
----------------
Lê os CSVs do DataJud e constrói:
  1. SQLite  — texto completo de cada decisão
  2. TF-IDF  — índice vetorial para busca semântica (modo padrão, offline)

Para usar OpenAI ou BERTimbau:
  export EMBEDDING_MODE=openai   (precisa de OPENAI_API_KEY)
  export EMBEDDING_MODE=bert     (precisa de sentence-transformers)

Execute:
  python rag/1_indexar.py
"""
import csv, sqlite3, hashlib, time, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

RAW_DIR    = Path("data/raw")
DB_DIR     = Path("data/rag")
DB_DIR.mkdir(parents=True, exist_ok=True)
SQLITE_PATH = DB_DIR / "jurisprudencia.db"
LIMITE_DOCS = None  # None = todos; ex: 50_000 para MVP

def criar_sqlite():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decisoes (
            id TEXT PRIMARY KEY, numero_processo TEXT, tribunal TEXT,
            segmento TEXT, assunto_codigo TEXT, assunto_nome TEXT,
            data_ajuizamento TEXT, valor_causa REAL, grau TEXT,
            orgao_julgador TEXT, ementa TEXT, label INTEGER
        )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_trib ON decisoes(tribunal)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ass  ON decisoes(assunto_codigo)")
    conn.commit()
    return conn

def id_unico(row):
    return hashlib.md5(f"{row.get('tribunal','')}_{row.get('numero_processo','')}".encode()).hexdigest()

def montar_ementa(row):
    partes = []
    if row.get("assunto_nome"):   partes.append(f"Assunto: {row['assunto_nome']}.")
    if row.get("tribunal"):        partes.append(f"Tribunal: {row['tribunal']}.")
    if row.get("classe_nome"):     partes.append(f"Classe: {row['classe_nome']}.")
    label = int(row.get("label", -1))
    if label == 1:  partes.append("Resultado: procedente. Pedido acolhido.")
    elif label == 0: partes.append("Resultado: improcedente. Pedido rejeitado.")
    if row.get("orgao_julgador"): partes.append(f"Órgão: {row['orgao_julgador']}.")
    grau = "primeira instância" if "G1" in str(row.get("grau","")) else "segunda instância"
    partes.append(f"Instância: {grau}.")
    return " ".join(partes)

def ler_csvs():
    arquivos = list(RAW_DIR.glob("*.csv"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV em {RAW_DIR}. Execute: python datajud/1_coletar_datajud.py")
    todos = []
    for arq in arquivos:
        with open(arq, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("label") in ("0","1"):
                    todos.append(row)
                    if LIMITE_DOCS and len(todos) >= LIMITE_DOCS:
                        break
        print(f"  Lido: {arq.name} → {len(todos)} registros")
        if LIMITE_DOCS and len(todos) >= LIMITE_DOCS:
            break
    return todos

def indexar():
    print("="*56)
    print("  RAG — Indexação de jurisprudência")
    print("="*56)

    docs = ler_csvs()
    print(f"\n  Total: {len(docs):,} decisões\n")

    # 1. SQLite
    print("  Populando SQLite...")
    conn = criar_sqlite()
    n_sql = 0
    for row in docs:
        doc_id = id_unico(row)
        ementa = montar_ementa(row)
        try:
            conn.execute("INSERT OR IGNORE INTO decisoes VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (doc_id, row.get("numero_processo",""), row.get("tribunal",""),
                 row.get("segmento",""), row.get("assunto_codigo",""),
                 row.get("assunto_nome",""), row.get("data_ajuizamento",""),
                 float(row.get("valor_causa",0) or 0), row.get("grau",""),
                 row.get("orgao_julgador",""), ementa, int(row.get("label",0))))
            n_sql += 1
        except Exception: pass
    conn.commit()
    print(f"  SQLite: {n_sql:,} decisões → {SQLITE_PATH}")

    # 2. TF-IDF (ou OpenAI/BERT se configurado)
    print("\n  Gerando índice de busca...")
    ids     = [id_unico(r) for r in docs]
    textos  = [montar_ementa(r) for r in docs]

    from rag.embedding import tfidf_fit, embedder_disponivel
    modo = embedder_disponivel()
    print(f"  Modo de embedding: {modo.upper()}")

    if modo == "tfidf":
        tfidf_fit(textos, ids)
    elif modo == "openai":
        from rag.embedding import openai_embed
        import numpy as np, pickle
        print("  Gerando embeddings via OpenAI (em lotes de 100)...")
        vetores, batch_size = [], 100
        for i in range(0, len(textos), batch_size):
            batch = textos[i:i+batch_size]
            vetores.extend(openai_embed(batch))
            print(f"  {min(i+batch_size,len(textos))}/{len(textos)}")
        arr = np.array(vetores, dtype="float32")
        with open(DB_DIR / "openai_vectors.pkl", "wb") as f:
            pickle.dump((arr, ids), f)
        print(f"  OpenAI: {len(vetores)} vetores salvos")
    elif modo == "bert":
        from rag.embedding import bert_embed
        import numpy as np, pickle
        vetores = bert_embed(textos)
        arr = np.array(vetores, dtype="float32")
        with open(DB_DIR / "bert_vectors.pkl", "wb") as f:
            pickle.dump((arr, ids), f)
        print(f"  BERT: {len(vetores)} vetores salvos")

    print(f"\n{'='*56}")
    print(f"  BASE PRONTA")
    print(f"  Decisões : {n_sql:,}")
    print(f"  Embedding: {modo.upper()}")
    print(f"  Arquivos : {DB_DIR}/")
    print(f"{'='*56}")
    print(f"\n  Próximo: python rag/2_buscar.py")

if __name__ == "__main__":
    indexar()
