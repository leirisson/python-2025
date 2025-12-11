# Classe Retângulo: Implemente uma classe Retangulo com atributos largura e altura.
# Adicione métodos para calcular área e perímetro.

class Retangulo:
    def __init__(self, largura:float, altura:float):
        self.largura = largura
        self.altura = altura
        
    def calcular_area(self):
        area = self.largura * self.altura
        return f"Area do trinagulo: {area:.2f}"
    
    
    def calcular_perimetro(self):
        perimetro = 2 * (self.largura + self.altura)
        return f"perimetro do triangulo: {perimetro:.2f}"