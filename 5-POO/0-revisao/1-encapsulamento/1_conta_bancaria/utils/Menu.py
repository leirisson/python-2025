



class Menu:
    def __init__(self,  opcoes: list, titulo: str):
        self.opcoes = opcoes
        self.titulo = titulo
        
    def menu_principal(self):
        self.titulo_sistema()
        for opcao in self.opcoes:
            print(opcao)
        
    def titulo_sistema(self):
        comprimento_linha = len(self.titulo)
        print("="*comprimento_linha)
        print(self.titulo)
        print("="*comprimento_linha)