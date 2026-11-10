import os
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine



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

