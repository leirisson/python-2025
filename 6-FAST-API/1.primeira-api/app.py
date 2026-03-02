import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/saudar/{nome}")
async def saudar(nome: str):
    print(type(nome))
    return{
        "mensagem": f"olá, {nome}"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=3001,
        reload=True
        )