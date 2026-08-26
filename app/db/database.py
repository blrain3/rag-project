"""Database engine and session management (SQLAlchemy 2.0)."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # 每次取连接前先 ping，防止用到已断开的连接
    pool_size=5,          # 连接池常驻连接数
    max_overflow=10,      # 高峰期允许额外超开的连接数
    echo=False,           # True 时打印所有 SQL，调试期很有用
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def check_db_connection() -> bool:
    """Test connectivity with a trivial query."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
