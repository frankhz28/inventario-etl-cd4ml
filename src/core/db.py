from sqlalchemy import create_engine
from src.core.config import settings

engine = create_engine(
    url=settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)