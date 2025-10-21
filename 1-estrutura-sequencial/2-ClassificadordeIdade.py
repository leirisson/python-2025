# 📋 Exercício 1: Classificador de Idade
# Contexto
# Criar sistema de classificação etária para cinema/jogos.
# Objetivo
# Classificar pessoa em categorias baseado na idade.
# Checklist

#  Solicitar idade do usuário
#  Classificar: Criança (0-12), Adolescente (13-17), Adulto (18-59), Idoso (60+)
#  Validar se idade é positiva
#  Informar benefícios da categoria (desconto, gratuidade)
#  Verificar se pode assistir filme 18+
#  Usar if/elif/else adequadamente
# ==================
# Saída Esperada
# ==================
# === CLASSIFICAÇÃO ETÁRIA ===
# Idade: 15

# Categoria: Adolescente
# Benefícios: Meia-entrada em cinemas
# Restrições: Filmes 18+ proibidos
# Pode entrar sozinho: Não (precisa acompanhante)

idade = int(input("Qual a sua idade: "))

if idade <= 12:
    print("=== CLASSIFICAÇÃO ETÁRIA ===")
    print("NÃO PODE ASSITIR FILMES +18")
    print("PRECISA DE ACOMPANHANTE")
elif idade >=13 and idade <= 17:
    print("=== CLASSIFICAÇÃO ETÁRIA ===")
    print("CATEGORIA: ADOLECENTE")
    print("VENEFÍCIO: MEIA-ENTRADA")
    print("FILME +18 PROIBIDO")
elif idade >=18 and idade <= 59:
    print("=== CLASSIFICAÇÃO ETÁRIA ===")
    print("NÃO PRECISA DE ACOMPANHANTE")
else: 
    print("=== CLASSIFICAÇÃO ETÁRIA ===")
    print("IDOSO.")