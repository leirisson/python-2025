# # Exercício 2: Calculadora de Multas de Trânsito
# # Contexto
# # Sistema para calcular multa baseada na velocidade do veículo.
# # Objetivo
# # Determinar tipo de multa e pontos na CNH conforme excesso de velocidade.
# # Checklist

# #  Solicitar velocidade permitida na via
# #  Solicitar velocidade do veículo
# #  Calcular excesso de velocidade
# #  Classificar infração: Leve (até 20%), Média (20-50%), Grave (50%+)
# #  Definir valor da multa: Leve (R$ 130), Média (R$ 195), Grave (R$ 880)
# #  Definir pontos na CNH: Leve (3), Média (5), Grave (7)
# #  Verificar suspensão se velocidade > 50% do limite

# === MULTA DE TRÂNSITO ===
# Limite: 60 km/h
# Velocidade: 85 km/h
# Excesso: 25 km/h (41.67%)

# INFRAÇÃO: Média
# Valor da multa: R$ 195.00
# Pontos na CNH: 5 pontos
# Status: Multa aplicada

velocidadePermitida = float(input("Qual a valocidade permitida na pista ?: "))
veloCidadeDoVeiculo = float(input("Qual a velocidade do veiculo ?: "))

infracaoLeve = 0.20 * velocidadePermitida
infracaoMedia = 0.50 * velocidadePermitida

if(veloCidadeDoVeiculo <= infracaoLeve):
    print(f"""
    ===============================
          MULTA DE TRANSITO
    ===============================
          INFRAÇÃO: LEVE
          VALOR: (R$ 130)
          PONTOS NA CNH: 3
""")
print(infracaoLeve, infracaoMedia)