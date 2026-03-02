from pydantic import BaseModel

class Usuario(BaseModel):
    nome: str
    idade: int
    altura: float
    ativo: bool = True
    

try:
    
    usuario = Usuario(nome="Leirisson", idade=27, altura=1.69)
    print(usuario.idade)
except Exception as e:
    print("erro de validação")
    print(e)