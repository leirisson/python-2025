from classes.Animal import Animal



class Gato(Animal):
    
    def fazer_som(self) -> str:
        return f"{self.nome} faz Miau Miau...."