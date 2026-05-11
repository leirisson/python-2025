"""
datajud/1_coletar_datajud.py
-----------------------------
Coleta processos da API pública DataJud (CNJ).
Cobre todos os Tribunais de Justiça estaduais (TJs)
e todos os Tribunais Regionais do Trabalho (TRTs).

Como usar:
  1. Configure sua API Key:
       export DATAJUD_API_KEY="sua_chave_aqui"
  2. Escolha o perfil de coleta em PERFIL_ATIVO abaixo
  3. Execute:
       python datajud/1_coletar_datajud.py

Para obter sua API Key (gratuita):
  -> https://datajud.cnj.jus.br -> Cadastre-se
  -> Meu Perfil -> API Key -> Gerar Nova Chave
"""

import asyncio
import aiohttp
import csv
import os
import time
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential

# ================================================================
#  CONFIGURACAO PRINCIPAL
# ================================================================

API_KEY  = os.getenv("DATAJUD_API_KEY", "SUA_CHAVE_AQUI")
BASE_URL = "https://api-publica.datajud.cnj.jus.br"

# Escolha o perfil:
#   "mvp"        -> 3 TJs grandes + 3 TRTs, 5k processos cada (inicio rapido)
#   "estaduais"  -> todos os 27 TJs, 10k cada
#   "trabalho"   -> todos os 24 TRTs, 10k cada
#   "completo"   -> TJs + TRTs, 10k cada (coleta maxima)
PERFIL_ATIVO = "mvp"

DATA_INICIO = "2020-01-01"
DATA_FIM    = "2024-12-31"

# Pausa entre paginas (respeita rate limit do CNJ)
PAUSA_ENTRE_PAGINAS = 0.5

# ================================================================
#  TRIBUNAIS ESTADUAIS — todos os 27 TJs
# ================================================================

TRIBUNAIS_ESTADUAIS = {
    # alias   : (nome,    UF)
    "tjsp"  : ("TJSP",   "SP"),
    "tjrj"  : ("TJRJ",   "RJ"),
    "tjmg"  : ("TJMG",   "MG"),
    "tjrs"  : ("TJRS",   "RS"),
    "tjpr"  : ("TJPR",   "PR"),
    "tjsc"  : ("TJSC",   "SC"),
    "tjba"  : ("TJBA",   "BA"),
    "tjpe"  : ("TJPE",   "PE"),
    "tjce"  : ("TJCE",   "CE"),
    "tjgo"  : ("TJGO",   "GO"),
    "tjpa"  : ("TJPA",   "PA"),
    "tjma"  : ("TJMA",   "MA"),
    "tjms"  : ("TJMS",   "MS"),
    "tjmt"  : ("TJMT",   "MT"),
    "tjrn"  : ("TJRN",   "RN"),
    "tjal"  : ("TJAL",   "AL"),
    "tjpi"  : ("TJPI",   "PI"),
    "tjse"  : ("TJSE",   "SE"),
    "tjro"  : ("TJRO",   "RO"),
    "tjam"  : ("TJAM",   "AM"),
    "tjto"  : ("TJTO",   "TO"),
    "tjap"  : ("TJAP",   "AP"),
    "tjac"  : ("TJAC",   "AC"),
    "tjrr"  : ("TJRR",   "RR"),
    "tjpb"  : ("TJPB",   "PB"),
    "tjes"  : ("TJES",   "ES"),
    "tjdft" : ("TJDFT",  "DF"),
}

# ================================================================
#  TRIBUNAIS DO TRABALHO — todos os 24 TRTs
# ================================================================

TRIBUNAIS_TRABALHO = {
    "trt1"  : ("TRT-1",  "RJ"),
    "trt2"  : ("TRT-2",  "SP"),
    "trt3"  : ("TRT-3",  "MG"),
    "trt4"  : ("TRT-4",  "RS"),
    "trt5"  : ("TRT-5",  "BA"),
    "trt6"  : ("TRT-6",  "PE"),
    "trt7"  : ("TRT-7",  "CE"),
    "trt8"  : ("TRT-8",  "PA/AP"),
    "trt9"  : ("TRT-9",  "PR"),
    "trt10" : ("TRT-10", "DF/TO"),
    "trt11" : ("TRT-11", "AM/RR"),
    "trt12" : ("TRT-12", "SC"),
    "trt13" : ("TRT-13", "PB"),
    "trt14" : ("TRT-14", "RO/AC"),
    "trt15" : ("TRT-15", "SP-int"),
    "trt16" : ("TRT-16", "MA"),
    "trt17" : ("TRT-17", "ES"),
    "trt18" : ("TRT-18", "GO"),
    "trt19" : ("TRT-19", "AL"),
    "trt20" : ("TRT-20", "SE"),
    "trt21" : ("TRT-21", "RN"),
    "trt22" : ("TRT-22", "PI"),
    "trt23" : ("TRT-23", "MT"),
    "trt24" : ("TRT-24", "MS"),
}

# ================================================================
#  ASSUNTOS POR SEGMENTO (codigos TPU do CNJ)
# ================================================================

ASSUNTOS_ESTADUAIS = [
    # -- Consumidor --------------------------------------------------
    7619,   # Dano Moral (responsabilidade civil)
    10949,  # Cobranca Indevida / Repeticao de Indebito
    9636,   # Indenizacao por Dano Material
    6201,   # Praticas Abusivas (CDC)
    7771,   # Rescisao do Contrato de Consumo
    # -- Civil -------------------------------------------------------
    10956,  # Indenizacao por Dano Moral (civel geral)
    6226,   # Cobranca de Divida
    7782,   # Despejo por Falta de Pagamento
    9507,   # Busca e Apreensao de Bem Alienado Fiduciariamente
    6218,   # Acidente de Transito
    6222,   # Obrigacao de Fazer / Nao Fazer
    # -- Familia -----------------------------------------------------
    9285,   # Alimentos
    9283,   # Divorcio Litigioso
    9289,   # Guarda e Responsabilidade
]

ASSUNTOS_TRABALHO = [
    # -- Remuneracao -------------------------------------------------
    1412,   # Horas Extras
    1407,   # Adicional de Insalubridade
    1408,   # Adicional de Periculosidade
    1413,   # Intervalo Intrajornada
    # -- Rescisao ----------------------------------------------------
    1399,   # Rescisao Indireta
    1401,   # Aviso Previo
    1403,   # FGTS (saldo / multa 40%)
    1406,   # Seguro Desemprego
    # -- Danos -------------------------------------------------------
    2493,   # Dano Moral (trabalhista)
    2643,   # Acidente de Trabalho / Doenca Ocupacional
    # -- Vinculo -----------------------------------------------------
    1396,   # Reconhecimento de Vinculo Empregaticio
    9532,   # Equiparacao Salarial
]

# ================================================================
#  PERFIS DE COLETA
# ================================================================

PERFIS = {
    "mvp": {
        "desc":     "MVP — 3 TJs + 3 TRTs, 5k por tribunal",
        "estaduais": ["tjsp", "tjrj", "tjmg"],
        "trabalho":  ["trt2", "trt3", "trt15"],
        "assuntos_estaduais": ASSUNTOS_ESTADUAIS[:6],
        "assuntos_trabalho":  ASSUNTOS_TRABALHO[:5],
        "limite": 5_000,
    },
    "estaduais": {
        "desc":     "Todos os 27 TJs — 10k por tribunal",
        "estaduais": list(TRIBUNAIS_ESTADUAIS.keys()),
        "trabalho":  [],
        "assuntos_estaduais": ASSUNTOS_ESTADUAIS,
        "assuntos_trabalho":  [],
        "limite": 10_000,
    },
    "trabalho": {
        "desc":     "Todos os 24 TRTs — 10k por tribunal",
        "estaduais": [],
        "trabalho":  list(TRIBUNAIS_TRABALHO.keys()),
        "assuntos_estaduais": [],
        "assuntos_trabalho":  ASSUNTOS_TRABALHO,
        "limite": 10_000,
    },
    "completo": {
        "desc":     "Todos os TJs + TRTs — 10k por tribunal",
        "estaduais": list(TRIBUNAIS_ESTADUAIS.keys()),
        "trabalho":  list(TRIBUNAIS_TRABALHO.keys()),
        "assuntos_estaduais": ASSUNTOS_ESTADUAIS,
        "assuntos_trabalho":  ASSUNTOS_TRABALHO,
        "limite": 10_000,
    },
}

# ================================================================
#  CAMPOS DO CSV DE SAIDA
# ================================================================

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MOVIMENTOS_DECISAO = {219, 237, 193, 11009, 26}

CAMPOS_CSV = [
    "numero_processo", "tribunal", "segmento",
    "classe_codigo", "classe_nome",
    "assunto_codigo", "assunto_nome",
    "data_ajuizamento", "valor_causa",
    "grau", "orgao_julgador", "municipio_ibge",
    "n_movimentos", "label",
]

# ================================================================
#  FUNCOES DE PROCESSAMENTO
# ================================================================

def extrair_resultado(movimentos):
    PROC    = ["julgo procedente","julgo totalmente procedente","dou provimento",
               "provejo o recurso","condeno o reu","condeno a re","acolho o pedido"]
    IMPROC  = ["julgo improcedente","julgo totalmente improcedente","nego provimento",
               "improcedente o pedido","indefiro o pedido","rejeito o pedido","denego"]
    PARCIAL = ["parcialmente procedente","procedente em parte",
               "acolho parcialmente","provejo em parte"]

    for mov in reversed(movimentos):
        if mov.get("codigo") not in MOVIMENTOS_DECISAO:
            continue
        c = mov.get("complemento", "").lower()
        if any(p in c for p in PARCIAL):
            return None
        if any(p in c for p in PROC) and not any(p in c for p in IMPROC):
            return 1
        if any(p in c for p in IMPROC) and not any(p in c for p in PROC):
            return 0
    return None


def processar_hit(hit, segmento):
    src  = hit.get("_source", {})
    movs = src.get("movimentos", [])
    lbl  = extrair_resultado(movs)
    if lbl is None:
        return None

    assuntos = src.get("assuntos", [{}])
    ass  = assuntos[0] if assuntos else {}
    orgao = src.get("orgaoJulgador", {})

    return {
        "numero_processo":  src.get("numeroProcesso", ""),
        "tribunal":         src.get("tribunal", ""),
        "segmento":         segmento,
        "classe_codigo":    src.get("classe", {}).get("codigo", ""),
        "classe_nome":      src.get("classe", {}).get("nome", ""),
        "assunto_codigo":   ass.get("codigo", ""),
        "assunto_nome":     ass.get("nome", ""),
        "data_ajuizamento": src.get("dataAjuizamento", "")[:10],
        "valor_causa":      src.get("valor", 0) or 0,
        "grau":             src.get("grau", "G1"),
        "orgao_julgador":   orgao.get("nome", ""),
        "municipio_ibge":   orgao.get("codigoMunicipioIBGE", ""),
        "n_movimentos":     len(movs),
        "label":            lbl,
    }


def montar_query(assunto_cod, search_after=None):
    # IMPORTANTE: o DataJud nao permite sort por _id (Fielddata disallowed).
    # Usamos dataAjuizamento + numeroProcesso como chave de paginacao.
    q = {
        "size": 100,
        "sort": [
            {"dataAjuizamento":  {"order": "asc"}},
            {"numeroProcesso":   {"order": "asc"}},   # <-- substitui _id
        ],
        "query": {"bool": {"must": [
            {"match": {"assuntos.codigo": assunto_cod}},
            {"range": {"dataAjuizamento": {"gte": DATA_INICIO, "lte": DATA_FIM}}},
        ]}},
        "_source": [
            "numeroProcesso","tribunal","classe","assuntos",
            "movimentos","dataAjuizamento","valor","grau","orgaoJulgador",
        ],
    }
    if search_after:
        q["search_after"] = search_after
    return q


@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=60), reraise=True)
async def buscar_pagina(session, tribunal, assunto_cod, search_after=None):
    url = f"{BASE_URL}/api_publica_{tribunal}/_search"
    hdrs = {"Authorization": f"APIKey {API_KEY}", "Content-Type": "application/json"}

    async with session.post(url, json=montar_query(assunto_cod, search_after), headers=hdrs) as r:
        if r.status == 429:
            print("      ⚠️  Rate limit — aguardando 60s...")
            await asyncio.sleep(60)
            raise Exception("Rate limit")
        if r.status == 404:
            return [], None
        if r.status != 200:
            raise Exception(f"HTTP {r.status}: {(await r.text())[:200]}")
        data = await r.json()

    hits = data.get("hits", {}).get("hits", [])
    return hits, (hits[-1].get("sort") if hits else None)


async def coletar_tribunal(session, alias, segmento, assuntos, limite, writer, lock):
    total = 0
    for assunto_cod in assuntos:
        if limite and total >= limite:
            break
        search_after = None
        while True:
            try:
                hits, next_sa = await buscar_pagina(session, alias, assunto_cod, search_after)
            except Exception as e:
                print(f"      ❌  {alias.upper()}/assunto {assunto_cod}: {e}")
                break
            if not hits:
                break

            linhas = [r for h in hits if (r := processar_hit(h, segmento))]
            async with lock:
                writer.writerows(linhas)
            total += len(linhas)

            if limite and total >= limite:
                break
            search_after = next_sa
            await asyncio.sleep(PAUSA_ENTRE_PAGINAS)
    return total


# ================================================================
#  MAIN
# ================================================================

async def main():
    cfg = PERFIS[PERFIL_ATIVO]
    n_tjs  = len(cfg["estaduais"])
    n_trts = len(cfg["trabalho"])

    print("=" * 62)
    print(f"  COLETA DataJud")
    print(f"  Perfil   : {cfg['desc']}")
    print(f"  TJs      : {n_tjs} tribunais ({', '.join(cfg['estaduais'][:5])}{'...' if n_tjs>5 else ''})")
    print(f"  TRTs     : {n_trts} tribunais ({', '.join(cfg['trabalho'][:5])}{'...' if n_trts>5 else ''})")
    print(f"  Periodo  : {DATA_INICIO} -> {DATA_FIM}")
    print(f"  Limite   : {cfg['limite']:,} processos/tribunal")
    print("=" * 62)

    if API_KEY == "SUA_CHAVE_AQUI":
        print("\n  ⚠️  Configure sua API Key:")
        print("      export DATAJUD_API_KEY='sua_chave'")
        print("      -> https://datajud.cnj.jus.br\n")
        return

    t0   = time.time()
    total = 0
    out   = OUTPUT_DIR / f"coleta_{PERFIL_ATIVO}.csv"
    lock  = asyncio.Lock()

    conn    = aiohttp.TCPConnector(limit=4)
    timeout = aiohttp.ClientTimeout(total=30)

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        writer.writeheader()

        async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
            # TJs estaduais
            for alias in cfg["estaduais"]:
                nome = TRIBUNAIS_ESTADUAIS[alias][0]
                print(f"\n  📂  {nome} (estadual)")
                n = await coletar_tribunal(
                    session, alias, "estadual",
                    cfg["assuntos_estaduais"], cfg["limite"], writer, lock
                )
                total += n
                print(f"      -> {n:,} processos classificados")

            # TRTs
            for alias in cfg["trabalho"]:
                nome = TRIBUNAIS_TRABALHO[alias][0]
                print(f"\n  📂  {nome} (trabalho)")
                n = await coletar_tribunal(
                    session, alias, "trabalho",
                    cfg["assuntos_trabalho"], cfg["limite"], writer, lock
                )
                total += n
                print(f"      -> {n:,} processos classificados")

    elapsed = time.time() - t0
    print(f"\n{'='*62}")
    print(f"  CONCLUIDO")
    print(f"  Total   : {total:,} processos")
    print(f"  Tempo   : {elapsed/60:.1f} min")
    print(f"  Arquivo : {out}")
    print(f"{'='*62}")
    print(f"\n  Proximo: python datajud/2_consolidar.py")


if __name__ == "__main__":
    asyncio.run(main())