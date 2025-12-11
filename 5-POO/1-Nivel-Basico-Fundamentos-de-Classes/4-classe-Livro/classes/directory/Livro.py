class Livro:
    def __init__(self, titulo: str, autor: str, numero_paginas: int):
        self.titulo = titulo
        self.autor = autor
        self.numero_paginas = numero_paginas
        
    def decricao_do_livro(self):
        return f"titulo: {self.titulo} | altor: {self.autor} | numero de paginas: {self.numero_paginas}"
    
    
