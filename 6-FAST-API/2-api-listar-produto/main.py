from typing import Union
from fastapi import FastAPI

app = FastAPI()

# produtos 
produtos = {
    1 : {
        "nome":"teclado",
        "descricao":"teclado gamer g10",
        "valor":250.50,
        "estoque":100
    }
}


@app.get("/produtos")
def get_all_products():
    return produtos

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("main:app", host="0.0.0.0", port=3005, debug=True, reload=True)
    