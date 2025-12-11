# Classe Produto: Crie uma classe Produto com nome, 
# preço e quantidade em estoque. Implemente 
# métodos para adicionar/remover estoque e calcular valor total.

from classes.Produto import Produto

def main():
    p1 = Produto("teclado", 150,3)
    p2 = Produto("mouse", 100,4)
    
    print("Estoque Atual")
    print(p1.estoque_atual())
    print(p2.estoque_atual())
    p1.adicionar(3)
    p1.remover(2)
    print(p1.estoque_atual())
    print("valor estoque p1: ", p1.calcular_valor_estoque())
    print("valor estoque p2: ", p2.calcular_valor_estoque())
    
    
    

if __name__=="__main__":
    main()