"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging
import os

logger = logging.getLogger(__name__)

# Получение DATABASE_URL из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://interview_user:interview_pass@postgres:5432/interview_db"
)

# Создание engine
# Для SQLite используем StaticPool
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Проверка соединения перед использованием
        pool_size=10,  # Размер пула соединений
        max_overflow=20,  # Максимальное количество дополнительных соединений
        echo=False  # Логирование SQL запросов (True для debug)
    )

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Dependency для получения сессии базы данных
    Использование:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Инициализация базы данных
    Создает все таблицы если их нет
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def drop_all_tables():
    """
    ВНИМАНИЕ: Удаляет все таблицы!
    Использовать только для тестирования
    """
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")
