from typing import Union
from fastapi import FastAPI # type: ignore

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello":"world"}


    # comando para start da aplicalção:
    # fastapi dev main.py
    # rota => http://127.0.0.1:8000
