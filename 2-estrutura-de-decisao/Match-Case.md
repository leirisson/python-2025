# Match/Case (Python 3.10+)
# Sistema de roteamento de atendimento
tipo_problema = "pagamento"

match tipo_problema:
    case "pagamento":
        departamento = "Financeiro"
        prioridade = "Alta"
    case "entrega":
        departamento = "Logística"
        prioridade = "Média"
    case "produto":
        departamento = "Suporte Técnico"
        prioridade = "Média"
    case "devolucao":
        departamento = "SAC"
        prioridade = "Alta"
    case _:
        departamento = "Atendimento Geral"
        prioridade = "Baixa"

print(f"Encaminhar para: {departamento} (Prioridade: {prioridade})")