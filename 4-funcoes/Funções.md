# Funções
# O que são?
Blocos de código reutilizáveis que executam uma tarefa específica. Recebem parâmetros (entrada) e podem retornar valores (saída).
# Uso no Mundo Real
Validar CPF, calcular impostos, formatar datas, enviar emails - qualquer operação que você repete no código deve ser uma função.
# Exemplos Contextualizados
# Função Básica

def calcular_imc(peso, altura):
    """Calcula o Índice de Massa Corporal"""
    imc = peso / (altura ** 2)
    return round(imc, 2)

# Uso

imc = calcular_imc(70, 1.75)
print(f"Seu IMC: {imc}")

# =============================================
# Função com Parâmetros Padrão
# =============================================
def enviar_email(destinatario, assunto, mensagem, urgente=False):
    """Simula envio de email"""
    prioridade = "ALTA" if urgente else "NORMAL"
    
    print(f"--- Email Enviado ---")
    print(f"Para: {destinatario}")
    print(f"Assunto: {assunto}")
    print(f"Prioridade: {prioridade}")
    print(f"Mensagem: {mensagem}")
    return True
# =================
# Uso
# =================
enviar_email("cliente@email.com", "Pedido Confirmado", "Seu pedido foi aprovado!")
enviar_email("suporte@email.com", "Bug Crítico", "Sistema fora do ar", urgente=True)

# ===================
# Função Lambda e Map
# ===================
# Converter preços de dólar para real
precos_dolar = [10.50, 25.00, 100.00, 5.99]
taxa_cambio = 5.20

# Usando lambda
converter = lambda preco: preco * taxa_cambio
precos_real = list(map(converter, precos_dolar))

print("Preços em Real:", [f"R$ {p:.2f}" for p in precos_real])

# ===============================
# Decoradores (Conceito Avançado)
# ===============================

import time

def medir_tempo(funcao):
    """Decorador que mede o tempo de execução"""
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = funcao(*args, **kwargs)
        fim = time.time()
        print(f"⏱ {funcao.__name__} executou em {fim - inicio:.4f}s")
        return resultado
    return wrapper

@medir_tempo
def processar_dados(n):
    """Simula processamento pesado"""
    total = sum(range(n))
    return total
# ===========
# Uso
# ===========
resultado = processar_dados(1000000)

