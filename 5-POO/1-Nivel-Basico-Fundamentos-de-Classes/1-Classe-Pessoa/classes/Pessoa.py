# Classe Pessoa: Crie uma classe Pessoa com atributos nome, idade e CPF. 
# Adicione métodos para exibir os dados e verificar se a pessoa é maior de idade.

class Pessoa:
    def __init__(self, nome:str, idade: int, cpf:str) -> None:
        self.nome = nome
        self.idade = idade
        self.cpf = cpf
    
    def exibir_info(self) -> str:
        return f"nome: {self.nome} | idade: {self.idade} | cpf: {self.cpf}"
    
    