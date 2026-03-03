class ContextoSimples:
    def __enter__(self):
        print("Iniciando conxão com o banco de dados")
        
    def __exit__(self, exc_type, exc, tb):
        print("Feachando conxão com o banco de dados")
        
        
with ContextoSimples() as cs:
    print("Executando comandos no banco de dados")