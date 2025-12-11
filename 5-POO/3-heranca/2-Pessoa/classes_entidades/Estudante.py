from classes_entidades.Pessoa import Pessoa

class Estudante(Pessoa):
    def __init__(self, nome: str, idade: int, matricula: str):
        super().__init__(nome, idade) # Chama o construtor da classe pai
        self.matricula = matricula
    
    def apresentar(self):
        return f"{super().apresentar()} e minha matrícula é {self.matricula}"