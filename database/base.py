import json
from pathlib import Path

from sqlalchemy import Column, Integer, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.config import SQLITE_DB_PATH, LOGLEVEL
import logging


def load_kind_of_work() -> dict:
    with open("data/kind_of_work.json") as f:
        return json.load(f)


def add_new_kind_of_work(id, kind_of_work):
    with open("data/kind_of_work.json") as f:
        data = json.load(f)
    data[id] = kind_of_work
    with open("data/kind_of_work.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


Base = declarative_base()

DATABASE_URL = f"sqlite+aiosqlite:///{SQLITE_DB_PATH}"

engine = create_async_engine(DATABASE_URL, echo=logging.DEBUG >= LOGLEVEL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    group_id = Column(Integer)

    def __repr__(self) -> str:
        return f"<User: {self.id}, {self.chat_id}, {self.group_id}>"


async def create_user(chat_id: int, group_id: int = None):
    async with async_session() as session:
        await session.execute(insert(User).values(chat_id=chat_id, group_id=group_id))
        await session.commit()


async def update_user(chat_id: int, new_group_id: int):
    async with async_session() as session:
        await session.execute(
            update(User).where(User.chat_id == chat_id).values(group_id=new_group_id)
        )
        await session.commit()


async def get_user(chat_id: int) -> User:
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


def get_events() -> list[dict]:
    if not Path("data/events.json").is_file():
        return []
    with open("data/events.json") as f:
        return json.load(f)


def add_event(event):
    if Path("data/events.json").is_file():
        with open("data/events.json") as f:

            data = json.load(f)
    else:
        data = []
    data.append(event)
    with open("data/events.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def remove_event(event_id):
    if Path("data/events.json").is_file():
        with open("data/events.json") as f:
            data: list = json.load(f)
        data = list(filter(lambda x: x["id"] != event_id, data))
        with open("data/events.json", "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
