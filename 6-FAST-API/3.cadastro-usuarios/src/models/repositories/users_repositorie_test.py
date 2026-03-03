import pytest
from .users_repositorie import UserRepositor

@pytest.mark.asyncio
async def test_insert_user():
    new_user = {
        "user_name": "Nomedetese",
        "age": 99,
        "uf":"SP"
    }
    
    repo = UserRepositor()
    await repo.insertUsers(new_user)
    