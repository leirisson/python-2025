from classes.Conta_Bancaria import Conta_bancaria
from utils.Menu import Menu

def main():
    
    titular = input("Qual o nome: ")
    saldo_inicial = float(input("Qual saldo inicial da conta: "))
    conta = Conta_bancaria(titular, saldo_inicial)
     
       
    valor_deposito = float(input("Qual valor deseja depositar: "))
    o_deposito_deu_certo = conta.depositar(valor_deposito) # realizando um deposito
    if o_deposito_deu_certo:
        print("Deposito realizado com secesso.")
      
    #realizando um deposito
    o_saque_deu_certo = conta.sacar(50)
    if o_saque_deu_certo:
        print("Saque realizado com sucesso !")

    
    print(conta.get_saldo())


if __name__ == "__main__":
    main()
    