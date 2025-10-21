# O que é?
São instruções executadas linha por linha, de cima para baixo, sem desvios ou repetições.
# Uso no Mundo Real
Quando você faz um cadastro em um site,
o sistema executa uma sequência: recebe os dados,
valida, salva no banco de dados e envia email de confirmação - tudo em ordem.

# Exemplo Contextualizado
# ==========================================
# Sistema de cálculo de frete
print("=== Sistema de Cálculo de Frete ===")

# Entrada de dados
peso = float(input("Peso do produto (kg): "))
distancia = float(input("Distância (km): "))
valor_produto = float(input("Valor do produto (R$): "))

# Processamento
taxa_base = 5.00
custo_por_kg = peso * 0.50
custo_por_km = distancia * 0.10
frete = taxa_base + custo_por_kg + custo_por_km

# Desconto para compras acima de R$ 200
if valor_produto > 200:
    frete = frete * 0.9  # 10% de desconto

# Saída
total = valor_produto + frete
print(f"\nValor do produto: R$ {valor_produto:.2f}")
print(f"Valor do frete: R$ {frete:.2f}")
print(f"Total a pagar: R$ {total:.2f}")