from classes.ContaBancaria import ContaBancaria


def main():
    conta = ContaBancaria("Leirisson", 150)
    print(conta.exebirSaldo())
    conta.depositar(200)
    print(conta.exebirSaldo())
    conta.sacar(240)

if __name__=="__main__":
    main()