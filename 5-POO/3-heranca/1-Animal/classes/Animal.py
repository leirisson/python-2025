class Animal:
    def __init__(self, nome: str):
        self.nome = nome
        
    def fazer_som(self) -> str:
        return "Som generico"