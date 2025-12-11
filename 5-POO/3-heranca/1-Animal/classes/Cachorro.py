from classes.Animal import Animal


class Cachorro(Animal):
    def fazer_som(self) -> str:
        return f"{self.nome} faz o som Au Au!"
    
