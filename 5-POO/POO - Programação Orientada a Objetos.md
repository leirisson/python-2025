# POO - Programação Orientada a Objetos
# O que é?
Paradigma de programação baseado em "objetos" que contêm dados (atributos) e comportamentos (métodos). Organiza o código de forma mais próxima ao mundo real.
# Uso no Mundo Real
Modelar sistemas complexos: usuários em uma rede social, produtos em um e-commerce, veículos em um app de transporte, contas bancárias, etc.

# Exemplos Contextualizados
# Classe Básica

class ContaBancaria:
    """Representa uma conta bancária"""
    
    def __init__(self, titular, saldo_inicial=0):
        self.titular = titular
        self.saldo = saldo_inicial
        self.transacoes = []
    
    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            self.transacoes.append(f"Depósito: +R$ {valor:.2f}")
            return True
        return False
    
    def sacar(self, valor):
        if 0 < valor <= self.saldo:
            self.saldo -= valor
            self.transacoes.append(f"Saque: -R$ {valor:.2f}")
            return True
        return False
    
    def extrato(self):
        print(f"\n=== Extrato - {self.titular} ===")
        print(f"Saldo atual: R$ {self.saldo:.2f}")
        print("\nÚltimas transações:")
        for transacao in self.transacoes[-5:]:
            print(f"  • {transacao}")

# Uso
conta = ContaBancaria("Maria Silva", 1000)
conta.depositar(500)
conta.sacar(200)
conta.extrato()

# ==============================================================
# Herança
# ==============================================================
class Produto:
    """Classe base para produtos"""
    
    def __init__(self, nome, preco, estoque):
        self.nome = nome
        self.preco = preco
        self.estoque = estoque
    
    def valor_total(self):
        return self.preco * self.estoque
    
    def info(self):
        return f"{self.nome} - R$ {self.preco:.2f} ({self.estoque} unidades)"

class ProdutoDigital(Produto):
    """Produto digital - não tem estoque físico"""
    
    def __init__(self, nome, preco, tamanho_mb):
        super().__init__(nome, preco, estoque=float('inf'))
        self.tamanho_mb = tamanho_mb
    
    def info(self):
        return f"{self.nome} - R$ {self.preco:.2f} (Digital - {self.tamanho_mb}MB)"

class ProdutoFisico(Produto):
    """Produto físico com peso e dimensões"""
    
    def __init__(self, nome, preco, estoque, peso_kg):
        super().__init__(nome, preco, estoque)
        self.peso_kg = peso_kg
    
    def calcular_frete(self, distancia_km):
        return self.peso_kg * 0.5 + distancia_km * 0.1
# ==============
# Uso
# ==============
ebook = ProdutoDigital("Python Completo", 49.90, 15)
notebook = ProdutoFisico("Notebook Dell", 3500, 10, 2.5)

print(ebook.info())
print(notebook.info())
print(f"Frete: R$ {notebook.calcular_frete(100):.2f}")

# ==================
# Encapsulamento
# ==================

class Usuario:
    """Usuário com senha protegida"""
    
    def __init__(self, username, senha):
        self.username = username
        self.__senha = senha  # Atributo privado
        self.__tentativas_login = 0
    
    def verificar_senha(self, senha):
        """Verifica senha com limite de tentativas"""
        if self.__tentativas_login >= 3:
            return False, "Conta bloqueada"
        
        if senha == self.__senha:
            self.__tentativas_login = 0
            return True, "Login realizado"
        else:
            self.__tentativas_login += 1
            return False, f"Senha incorreta ({3 - self.__tentativas_login} tentativas restantes)"
    
    def alterar_senha(self, senha_antiga, senha_nova):
        """Altera a senha"""
        if senha_antiga == self.__senha:
            self.__senha = senha_nova
            return True
        return False
# =============
# Uso
# =============

usuario = Usuario("joao123", "senha_secreta")
sucesso, mensagem = usuario.verificar_senha("senha_errada")
print(mensagem)

# =========================================
#  Polimorfismo
# =========================================
class FormaPagamento:
    """Classe abstrata para formas de pagamento"""
    
    def processar(self, valor):
        raise NotImplementedError("Método deve ser implementado")

class CartaoCredito(FormaPagamento):
    def __init__(self, numero, parcelas=1):
        self.numero = numero[-4:]  # Últimos 4 dígitos
        self.parcelas = parcelas
    
    def processar(self, valor):
        valor_parcela = valor / self.parcelas
        return f"Cartão ****{self.numero}: {self.parcelas}x de R$ {valor_parcela:.2f}"

class Pix(FormaPagamento):
    def __init__(self, chave):
        self.chave = chave
    
    def processar(self, valor):
        return f"PIX para {self.chave}: R$ {valor:.2f} (instantâneo)"

class Boleto(FormaPagamento):
    def processar(self, valor):
        return f"Boleto gerado: R$ {valor:.2f} (vence em 3 dias)"

# Uso - mesma interface, comportamentos diferentes
def finalizar_compra(valor, forma_pagamento):
    print(forma_pagamento.processar(valor))

finalizar_compra(300, CartaoCredito("1234567890123456", 3))
finalizar_compra(300, Pix("joao@email.com"))
finalizar_compra(300, Boleto())

