from datetime import datetime
from db import Base
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, List
from sqlalchemy import ForeignKey, String,BigInteger,Integer, text

class Users(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger,unique=True,nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    amount: Mapped[int] = mapped_column(Integer,server_default=text("0"), nullable=False)
    last_visit: Mapped[Optional[datetime]] = mapped_column(server_default=text("CURRENT_TIMESTAMP"), nullable=True)
    
