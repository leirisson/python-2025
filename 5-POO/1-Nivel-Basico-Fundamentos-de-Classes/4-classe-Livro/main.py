# Classe Livro: Faça uma classe Livro com título, autor e número de páginas. 
# Adicione um método para exibir informações do livro.

from classes.directory.Livro import Livro

def main():
    livro = Livro("Conto dos contos","Leirisson Souza", 150)
    
    print(livro.decricao_do_livro())

if __name__=="__main__":
    main()
