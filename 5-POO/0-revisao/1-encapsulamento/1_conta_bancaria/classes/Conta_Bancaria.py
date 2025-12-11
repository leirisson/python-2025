class Conta_bancaria:
    def __init__(self, titular: str, saldo_inicial: float=0):
        self.titular = titular
        self.__saldo = saldo_inicial

    def depositar(self, valor:float) -> bool:
        if valor > 0:
            self.__saldo += valor
            return True
        return False
    
    def sacar(self, valor: float) -> bool:
        if 0 < valor <= self.__saldo:
            self.__saldo -= valor
            return True
        return False
    
    def get_saldo(self) -> float:
        return self.__saldo