"""
jurimetria/coleta/testar_conexao.py
------------------------------------
Testa a API Key e a conexão com o DataJud ANTES de iniciar a coleta.
Faz apenas 1 requisição por tribunal configurado.

Execute:  python -m jurimetria.coleta.testar_conexao
"""

import asyncio
import os
import sys

import aiohttp
from dotenv import load_dotenv
from pathlib import Path

# Força UTF-8 no stdout para suportar emojis no Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

API_KEY  = os.getenv("DATAJUD_API_KEY", "SUA_CHAVE_AQUI")
BASE_URL = "https://api-publica.datajud.cnj.jus.br"

TRIBUNAIS_TESTE = ["tjsp", "trt2"]


async def testar_tribunal(session: aiohttp.ClientSession, tribunal: str) -> bool:
    url     = f"{BASE_URL}/api_publica_{tribunal}/_search"
    headers = {"Authorization": f"APIKey {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "size":  1,
        "query": {"match_all": {}},
        "sort":  [{"dataAjuizamento": {"order": "desc"}}],
    }

    try:
        async with session.post(url, json=payload, headers=headers,
                                timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 401:
                print(f"  ❌  {tribunal.upper()}: API Key inválida ou expirada (HTTP 401)")
                return False
            if resp.status == 403:
                print(f"  ❌  {tribunal.upper()}: Acesso negado (HTTP 403)")
                return False
            if resp.status != 200:
                print(f"  ❌  {tribunal.upper()}: Erro HTTP {resp.status}")
                return False

            data  = await resp.json()
            total = data.get("hits", {}).get("total", {}).get("value", 0)
            hits  = data.get("hits", {}).get("hits", [])

            if hits:
                exemplo = hits[0].get("_source", {})
                num     = exemplo.get("numeroProcesso", "—")
                data_aj = exemplo.get("dataAjuizamento", "—")[:10]
                print(f"  ✅  {tribunal.upper()}: {total:,} processos indexados")
                print(f"      Exemplo: {num} — ajuizado em {data_aj}")
            else:
                print(f"  ✅  {tribunal.upper()}: Conexão OK (sem resultados na query)")
            return True

    except aiohttp.ClientConnectorError:
        print(f"  ❌  {tribunal.upper()}: Sem conexão com a internet ou API offline")
        return False
    except Exception as e:
        print(f"  ❌  {tribunal.upper()}: {e}")
        return False


async def main():
    print("=" * 52)
    print("  TESTE DE CONEXÃO — DataJud API")
    print("=" * 52)

    if API_KEY == "SUA_CHAVE_AQUI":
        print("""
  ⚠️  API Key não configurada!

  Configure em 0-jus/.env:
      DATAJUD_API_KEY=sua_chave_aqui

  Para obter sua chave (gratuita):
      https://datajud.cnj.jus.br -> Cadastre-se -> Meu Perfil -> API Key
""")
        return

    print(f"\n  API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"  Tribunais: {', '.join(t.upper() for t in TRIBUNAIS_TESTE)}\n")

    async with aiohttp.ClientSession() as session:
        resultados = []
        for tribunal in TRIBUNAIS_TESTE:
            ok = await testar_tribunal(session, tribunal)
            resultados.append(ok)
            await asyncio.sleep(0.5)

    print(f"\n{'='*52}")
    if all(resultados):
        print("  ✅  Tudo OK! Próximo passo:")
        print("      python -m jurimetria.coleta.coletar_datajud")
    else:
        print("  ❌  Corrija os erros acima antes de coletar.")
    print("=" * 52)


if __name__ == "__main__":
    asyncio.run(main())
