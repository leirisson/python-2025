from sqlalchemy import insert
from src.models.entities.users import Users
from src.models.settings.database_connection_handler import DBConnectionHandler

class UserRepositor:
    async def insertUsers(self, user_info: dict) -> None:
     async with DBConnectionHandler() as db:
         query = insert(Users).values(**user_info)
         await db.session.execute(query)
         await db.session.commit()
         