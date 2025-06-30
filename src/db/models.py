from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class BaseModel(DeclarativeBase):
    pass


class URLModel(BaseModel):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)

    url: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hits: Mapped[int] = mapped_column(Integer(), default=0, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    opaque: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    password: Mapped[str] = mapped_column(String(), nullable=True)

    modified: Mapped[datetime] = mapped_column(DateTime(), default=lambda: datetime.now(), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime(), default=lambda: datetime.now(),  nullable=False)