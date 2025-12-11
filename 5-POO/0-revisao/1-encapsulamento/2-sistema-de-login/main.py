from classes.Login import Login


def main():
    nome = input("qual o nome: ")
    senha = input("qual a senha: ")
    
    login = Login(nome, senha)
    
    
    print(login.alterar_senha("123",1234))
    

if __name__ == "__main__":
    main()
    