# 4. Estrutura de Repetição
# O que é?
Permite executar um bloco de código múltiplas vezes, seja por um número definido de iterações ou enquanto uma condição for verdadeira.
# Uso no Mundo Real
Processar uma lista de pedidos, enviar emails para múltiplos clientes, calcular médias de vendas, ler arquivos linha por linha - loops são fundamentais.
# Exemplos Contextualizados
# For Loop

# Processamento de pedidos em lote
pedidos = [
    {"id": 1001, "valor": 150.00, "status": "pendente"},
    {"id": 1002, "valor": 89.90, "status": "pendente"},
    {"id": 1003, "valor": 320.00, "status": "pendente"}
]

total_processado = 0

for pedido in pedidos:
    print(f"Processando pedido #{pedido['id']}...")
    pedido["status"] = "processado"
    total_processado += pedido["valor"]

print(f"\n✓ {len(pedidos)} pedidos processados")
print(f"Total: R$ {total_processado:.2f}")

# While Loop
# =================================
# Sistema de tentativas de login
tentativas = 0
max_tentativas = 3
senha_correta = "python123"

while tentativas < max_tentativas:
    senha = input(f"Digite a senha (Tentativa {tentativas + 1}/{max_tentativas}): ")
    
    if senha == senha_correta:
        print("✓ Login realizado com sucesso!")
        break
    else:
        tentativas += 1
        if tentativas < max_tentativas:
            print(f"✗ Senha incorreta. Você tem {max_tentativas - tentativas} tentativa(s) restante(s).")
        else:
            print("✗ Conta bloqueada. Entre em contato com o suporte.")

# ==============================================================================
# List Comprehension
# Aplicar desconto em produtos de uma categoria

produtos = [
    {"nome": "Notebook", "preco": 3000, "categoria": "eletrônicos"},
    {"nome": "Mouse", "preco": 50, "categoria": "eletrônicos"},
    {"nome": "Cadeira", "preco": 800, "categoria": "móveis"}
]

# Aplicar 15% de desconto em eletrônicos
produtos_desconto = [
    {**p, "preco": p["preco"] * 0.85} 
    if p["categoria"] == "eletrônicos" 
    else p 
    for p in produtos
]

for p in produtos_desconto:
    print(f"{p['nome']}: R$ {p['preco']:.2f}")

