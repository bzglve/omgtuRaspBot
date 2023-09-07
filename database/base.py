import json
from typing import Dict

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.orm.decl_api import DeclarativeMeta

from config.config import SQLITE_DB_PATH, LOGLEVEL
import logging


def load_kind_of_work() -> Dict[str, str]:
    with open("data/kind_of_work.json") as f:
        return dict(json.load(f))


def add_new_kind_of_work(id: str, kind_of_work: str):
    with open("data/kind_of_work.json") as f:
        data = json.load(f)
    data[id] = kind_of_work
    with open("data/kind_of_work.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


Base: DeclarativeMeta = declarative_base()

DATABASE_URL = f"sqlite+aiosqlite:///{SQLITE_DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=logging.DEBUG >= LOGLEVEL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    group_id: Mapped[int]

    def __repr__(self) -> str:
        return f"<User: {self.id}, {self.chat_id}, {self.group_id}>"


async def create_user(chat_id: int, group_id: int):
    async with async_session() as session:
        await session.execute(insert(User).values(chat_id=chat_id, group_id=group_id))
        await session.commit()


async def update_user(chat_id: int, new_group_id: int):
    async with async_session() as session:
        await session.execute(update(User).where(User.chat_id == chat_id).values(group_id=new_group_id))
        await session.commit()


async def get_user(chat_id: int) -> User:  # sourcery skip: raise-specific-error
    async with async_session() as session:
        users = list(await session.execute(select(User).where(User.chat_id == chat_id)))
        if len(users) == 1:
            return list(users[0])[0]
        elif not users:
            return User()
        else:
            raise Exception("Unexpected user query")


async def delete_user(chat_id: int):
    async with async_session() as session:
        await session.execute(delete(User).where(User.chat_id == chat_id))
        await session.commit()


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
