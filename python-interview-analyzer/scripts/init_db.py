#!/usr/bin/env python3
"""
Database initialization script
Создает все таблицы в базе данных
"""

import sys
import os
import logging

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import init_db, engine
from app.db.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Инициализация базы данных"""
    try:
        logger.info("Starting database initialization...")

        # Создание всех таблиц
        logger.info("Creating database tables...")
        init_db()

        # Проверка созданных таблиц
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        logger.info(f"Successfully created {len(tables)} tables:")
        for table in tables:
            logger.info(f"  ✓ {table}")

        logger.info("Database initialization completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
