# arquivo de conxão com o banco de dados
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Optional


CONNECTION_STRING = f"sqlite+aiosqlite:///schema.bd"

engine = create_async_engine(
    CONNECTION_STRING,
    echo=False,
    pool_size=2,
    max_overflow=0,
    pool_timeout=30
    )


async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class DBConnectionHandler:
    def __init__(self) -> None:
        self.session: Optional[AsyncSession] = None
    
    async def __aenter__(self): # inicia uma sessão para entrar no banco
        self.session = async_session()
        return self
    
    async def __aexit__(self, exc_type, exc, tb): # fecha a sessão do banco
        await self.session.close()