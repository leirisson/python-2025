print("=== sistema de cálculo de frete ===")
 
# ENTRADA DE  DADOS
peso = float(input("Peso do produto (kg): "))
distancia = float(input("Distância em (km): "))
valor_produto = float(input("Valor do produto (R$): "))

# PROCESSAMENTO
taxa_base = 5.00
custo_por_kg = peso * 0.50
custo_por_km = distancia * 0.10
frete = taxa_base + custo_por_kg + custo_por_km

# DESCONTO PARA COMPRAS ACIMA DE R$ 200
if valor_produto > 200:
    frete = frete * 0.9 #10% de deconto

# SAÍDA
total = valor_produto + frete
print(f"\n valor do produto: R$ {valor_produto:.2f}")
print(f"\n valor do frete: R$ {frete:.2f}")
print(f"TOTOAL A PAGAR: R$ {total}")