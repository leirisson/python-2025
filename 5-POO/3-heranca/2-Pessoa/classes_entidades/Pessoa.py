class Pessoa:
    def __init__(self, nome:str, idade:int) -> None:
        self.nome = nome
        self.idade = idade
        
    def apresentar(self):
        return f"olá, meu nome é {self.nome}"