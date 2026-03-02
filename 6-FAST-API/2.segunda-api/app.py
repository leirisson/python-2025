import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

class Usuario(BaseModel):
    nome: str
    idade: int
    altura: float
    ativo: bool = True


app = FastAPI()



@app.get("/saudacao/{nome}")
async def saudar(nome: str):
    print(type(nome))
    return {"mensagem": f"olá, {nome}"}

@app.post("/usuarios")
async def criar_usuario(usuario: Usuario):
    return{
        "mensagem": "usuario criado",
        "dados" : dict(usuario)
    }
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=3001,
        reload=True
    )