import asyncio 


async def task(nome, duracao):
    print(f"tarefa[{nome}] iniciando...")
    await asyncio.sleep(duracao)
    print(f"tarefa [{nome}] terminou ...")


async def main():
    await task("comprar pão", 5)

if __name__ == "__main__":
    asyncio.run(main())