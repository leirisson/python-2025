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

@app.get("/produtos/{id_produto}")
async def get_product_by_id(id_produto: int):
    produto_encontrado = produtos[id_produto]
    print(produto_encontrado)
    return produto_encontrado


if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("main:app", host="0.0.0.0", port=3005, debug=True, reload=True)
    