# 3. Estrutura de Decisão
*** O que é? ***
Permite que o programa tome decisões e execute diferentes blocos de código baseado em condições.
*** Uso no Mundo Real ***
Sistemas de autenticação, aprovação de crédito, categorização de produtos, validação de formulários - tudo usa estruturas de decisão.

*** Exemplos Contextualizados ***

*** If/Elif/Else ***
# Sistema de classificação de clientes por fidelidade
pontos = 850

if pontos >= 1000:
    categoria = "Diamante"
    desconto = 0.20
elif pontos >= 500:
    categoria = "Ouro"
    desconto = 0.15
elif pontos >= 200:
    categoria = "Prata"
    desconto = 0.10
else:
    categoria = "Bronze"
    desconto = 0.05

print(f"Categoria: {categoria}")
print(f"Desconto disponível: {desconto * 100}%")

*** Operadores Lógicos ***

# Validação de elegibilidade para promoção
idade = 25
is_cadastrado = True
compras_anteriores = 3

# Promoção válida para maiores de 18, cadastrados e com pelo menos 2 compras
elegivel = idade >= 18 and is_cadastrado and compras_anteriores >= 2

if elegivel:
    print("✓ Você está elegível para a promoção!")
else:
    print("✗ Você não atende aos requisitos da promoção.")