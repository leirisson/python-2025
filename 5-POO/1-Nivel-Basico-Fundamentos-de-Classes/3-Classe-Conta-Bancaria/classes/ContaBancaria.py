# Classe Conta Bancária: Crie uma classe ContaBancaria com atributos titular e saldo. 
# Implemente métodos para depositar, sacar e exibir saldo.

class ContaBancaria:
    def __init__(self, titular: str, saldo: float=0):
        self.titular = titular
        self.saldo = saldo
        
    def depositar(self, valor: float):
        if valor <=0:
            raise Exception(f"⚠ O valor: {valor} não deve ser igual o menor que zero.")
        self.saldo += valor
        print("Valor depositado com sucesso ✅")
        print(self.exebirSaldo())
        
    def sacar(self, valor: float):
        if valor > self.saldo:
            raise Exception("⚠ Saldo insuficiente para realizar o saque.")
        self.saldo -= valor
        print("Saque realizado com sucesso !: ✅")
        print(self.exebirSaldo())
    
    def exebirSaldo(self):
        return f"Saldo da conta: {self.saldo}"