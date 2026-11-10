import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, List
from sqlalchemy import ForeignKey, String,BigInteger,Integer, text



class Base(DeclarativeBase):
    pass

load_dotenv()

def connect_db():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

engine = create_async_engine(connect_db(), echo =True)

class Users(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger,unique=True,nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    amount: Mapped[int] = mapped_column(Integer,server_default=text("0"), nullable=False)
    last_visit: Mapped[Optional[datetime]] = mapped_column(server_default=text("CURRENT_TIMESTAMP"), nullable=True)
    

print(engine)