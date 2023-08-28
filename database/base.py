import asyncio
from datetime import datetime
import json
import logging
from hashlib import sha256
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config.config import LOGLEVEL, SQLITE_DB_PATH


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
    events = relationship("Event", cascade="all, delete")

    def __repr__(self) -> str:
        return f"<User: {self.id}, {self.chat_id}, {self.group_id}>"


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    hash = Column(String(256), unique=True, nullable=False)
    chat_id = Column(
        Integer, ForeignKey("users.chat_id", ondelete="CASCADE"), nullable=False
    )
    chat = relationship("User", back_populates="events")
    update_interval = Column(Integer, CheckConstraint("update_interval > 0"))
    last_update = Column(DateTime)
    enabled = Column(Boolean, default=True)
    function_id = Column(Integer)

    def __init__(self, chat_id:int, update_interval:int, last_update:datetime, function_id):
        self.hash = sha256()

    def __repr__(self) -> str:
        return f"<Event: {self.id}, {self.chat_id}, {self.update_interval}, {self.last_update}, {self.enabled}, {self.function_id}"  # noqa


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
        user = (await session.execute(select(User).where(User.chat_id == chat_id))).scalars().one_or_none()
        return user or User()


async def delete_user(chat_id: int):
    async with async_session() as session:
        await session.execute(delete(User).where(User.chat_id == chat_id))
        await session.execute(delete(Event).where(Event.chat_id == chat_id))
        await session.commit()


async def get_events(user: User = None) -> list[Event]:
    async with async_session() as session:
        return (
            (await session.execute(select(Event))).scalars().all()
            if user is None
            else (
                await session.execute(
                    select(Event).where(Event.chat_id == user.chat_id)
                )
            )
            .scalars()
            .all()
        )


async def create_event(event: Event):
    async with async_session() as session:
        session.add(event)
        await session.commit()


async def remove_event(event_hash: str):
    async with async_session() as session:
        await session.execute(delete(Event).where(Event.hash == event_hash))
        await session.commit()


async def update_event(event_hash: str, **kwargs):
    async with async_session() as session:
        await session.execute(
            update(Event).where(Event.hash == event_hash).values(**kwargs)
        )
        await session.commit()
