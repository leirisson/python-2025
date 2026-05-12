"""
rag/3_peticao_com_rag.py
------------------------
Integra o RAG com o LLM para gerar petições fundamentadas
com jurisprudência real da base DataJud.

Fluxo:
  1. Recebe os dados do caso
  2. Busca precedentes relevantes no ChromaDB
  3. Monta prompt com os precedentes como contexto
  4. LLM gera a petição citando jurisprudência real

Execute:
  python rag/3_peticao_com_rag.py

Ou importe a função gerar_peticao() no seu backend.
"""

import os
from pathlib import Path

# Importa o motor de busca
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from rag.buscar import buscar_precedentes, formatar_para_prompt

try:
    import anthropic
    USAR_ANTHROPIC = True
except ImportError:
    USAR_ANTHROPIC = False

# Para instalar: pip install anthropic
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# ── Mapeamento de tipo de ação para segmento ─────────────────────────

SEGMENTO_POR_TIPO = {
    "dano_moral_consumidor": "estadual",
    "cobranca_indevida":     "estadual",
    "acidente_transito":     "estadual",
    "despejo":               "estadual",
    "horas_extras":          "trabalho",
    "rescisao_indireta":     "trabalho",
    "adicional_insalubridade": "trabalho",
    "acidente_trabalho":     "trabalho",
    "beneficio_inss":        "estadual",
}


def montar_query_rag(caso: dict) -> str:
    """
    Transforma os dados do caso em uma query rica para o RAG.
    Quanto mais contexto, melhor a busca semântica.
    """
    partes = []

    if caso.get("tipo_acao"):
        partes.append(caso["tipo_acao"].replace("_", " "))

    if caso.get("fatos"):
        # Usa os primeiros 300 chars dos fatos — suficiente para embedding
        partes.append(caso["fatos"][:300])

    if caso.get("pedidos"):
        partes.append(caso["pedidos"][:150])

    return ". ".join(partes)


def gerar_peticao(caso: dict) -> dict:
    """
    Gera uma petição inicial fundamentada com jurisprudência real.

    Parâmetro 'caso' esperado:
      tipo_acao  : str  (ex: "dano_moral_consumidor")
      tribunal   : str  (ex: "TJSP")
      autor      : str
      reu        : str
      valor      : str  (ex: "20.000,00")
      fatos      : str  (texto livre)
      pedidos    : str  (texto livre)

    Retorna:
      peticao    : str  (texto completo da petição)
      precedentes: list (precedentes usados como base)
      n_prec     : int  (quantidade de precedentes encontrados)
    """
    tipo    = caso.get("tipo_acao", "")
    segmento = SEGMENTO_POR_TIPO.get(tipo, None)

    # ── 1. Busca jurisprudência relevante ────────────────────────────
    query = montar_query_rag(caso)
    precedentes = buscar_precedentes(
        query,
        n_resultados=5,
        segmento=segmento,
    )

    # Separa procedentes e improcedentes para dar contexto ao LLM
    proc   = [p for p in precedentes if p["resultado"] == "Procedente"]
    improc = [p for p in precedentes if p["resultado"] == "Improcedente"]

    contexto_juri = formatar_para_prompt(precedentes)

    taxa_proc = round(len(proc) / len(precedentes) * 100) if precedentes else 0

    # ── 2. Monta o prompt ────────────────────────────────────────────
    prompt = f"""Você é um advogado especialista em direito brasileiro com 20 anos de experiência.
Gere uma petição inicial completa, profissional e bem fundamentada.

═══════════════════════════════════════════════════
DADOS DO CASO
═══════════════════════════════════════════════════
Tipo de ação : {tipo.replace("_", " ").title()}
Tribunal     : {caso.get("tribunal", "")}
Autor        : {caso.get("autor", "")}
Réu          : {caso.get("reu", "")}
Valor        : R$ {caso.get("valor", "0,00")}

FATOS:
{caso.get("fatos", "")}

PEDIDOS:
{caso.get("pedidos", "")}

═══════════════════════════════════════════════════
JURISPRUDÊNCIA RELEVANTE (encontrada por IA na base DataJud)
Taxa de procedência em casos similares: {taxa_proc}%
═══════════════════════════════════════════════════
{contexto_juri}

═══════════════════════════════════════════════════
INSTRUÇÕES PARA A PETIÇÃO
═══════════════════════════════════════════════════
1. Estruture: Endereçamento → Qualificação → DOS FATOS → DO DIREITO → DOS PEDIDOS → Valor da causa
2. Na seção DO DIREITO:
   - Cite os artigos de lei pertinentes (CDC, CLT, CF/88, CC)
   - USE os precedentes acima para fundamentar (mencione o tribunal e resultado)
   - Se a taxa de procedência for alta (>60%), destaque isso como tendência jurisprudencial
3. Nos PEDIDOS: inclua principal, subsidiários e tutela de urgência se cabível
4. Linguagem jurídica formal — máximo 900 palavras
5. Termine com: "Termos em que pede deferimento."
"""

    # ── 3. Chama o LLM ───────────────────────────────────────────────
    if USAR_ANTHROPIC and API_KEY:
        client = anthropic.Anthropic(api_key=API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1800,
            messages=[{"role": "user", "content": prompt}],
        )
        texto_peticao = message.content[0].text
    else:
        # Modo demonstração — retorna o prompt montado para ver como ficaria
        texto_peticao = (
            "[MODO DEMONSTRAÇÃO — configure ANTHROPIC_API_KEY para gerar o texto]\n\n"
            f"O prompt montado com {len(precedentes)} precedentes reais seria:\n\n"
            + prompt[:800] + "..."
        )

    return {
        "peticao":      texto_peticao,
        "precedentes":  precedentes,
        "n_precedentes": len(precedentes),
        "taxa_procedencia": taxa_proc,
        "query_usada":  query[:100],
    }


# ── Teste ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 56)
    print("  Geração de petição com RAG + LLM")
    print("=" * 56)

    caso_teste = {
        "tipo_acao": "dano_moral_consumidor",
        "tribunal":  "TJSP",
        "autor":     "Maria Aparecida Lima",
        "reu":       "Banco Nacional S.A.",
        "valor":     "20.000,00",
        "fatos": (
            "A autora é correntista do banco réu há 10 anos. "
            "Em março de 2024 constatou cobranças indevidas de tarifas "
            "não contratadas no valor de R$ 347,00 mensais por 6 meses. "
            "Acionou o SAC três vezes sem resolução. "
            "Os débitos geraram saldo negativo e negativação indevida."
        ),
        "pedidos": (
            "Devolução em dobro dos valores (R$ 4.164,00), "
            "danos morais de R$ 15.000,00 e tutela de urgência "
            "para cessar as cobranças e excluir a negativação."
        ),
    }

    resultado = gerar_peticao(caso_teste)

    print(f"\n  Precedentes encontrados : {resultado['n_precedentes']}")
    print(f"  Taxa de procedência     : {resultado['taxa_procedencia']}%")
    print(f"\n  Precedentes usados:")
    for p in resultado["precedentes"]:
        print(f"    [{p['similaridade']}%] {p['tribunal']} — {p['resultado']}")

    print(f"\n{'─'*56}")
    print("  PETIÇÃO GERADA:")
    print("─" * 56)
    print(resultado["peticao"][:1200])
    if len(resultado["peticao"]) > 1200:
        print(f"\n  ... ({len(resultado['peticao'])} caracteres no total)")
