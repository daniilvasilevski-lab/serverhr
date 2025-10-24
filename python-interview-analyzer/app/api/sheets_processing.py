"""
API endpoints для обработки интервью из Google Sheets
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sheets", tags=["Google Sheets Processing"])


class ProcessSheetsResponse(BaseModel):
    success: bool
    message: str
    stats: Dict[str, int]


class UnprocessedInterviewsResponse(BaseModel):
    success: bool
    count: int
    interviews: List[Dict[str, Any]]


@router.post("/process-all", response_model=ProcessSheetsResponse)
async def process_all_interviews(background_tasks: BackgroundTasks):
    """
    Запуск обработки всех необработанных интервью из Google Sheets

    Этот endpoint:
    1. Сканирует входную Google таблицу
    2. Находит все строки где Processed != 1
    3. Запускает анализ каждого интервью
    4. Сохраняет результаты в выходную таблицу
    5. Отмечает строки как обработанные (Processed = 1)

    Returns:
        Статистика обработки: найдено, обработано, ошибок
    """
    try:
        from ..services.google_sheets_integration import get_sheets_integration
        from ..services.integrated_analyzer import IntegratedInterviewAnalyzer
        from ..services.cv_analyzer import CVAnalyzer
        from ..services.questions_analyzer import QuestionsAnalyzer
        import openai
        from ..config.settings import settings

        logger.info("🚀 Starting Google Sheets processing...")

        # Инициализация сервисов
        sheets_service = get_sheets_integration()

        openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        analyzer = IntegratedInterviewAnalyzer(openai_client)
        cv_analyzer = CVAnalyzer(openai_client)
        questions_analyzer = QuestionsAnalyzer(openai_client)

        # Запуск обработки
        stats = await sheets_service.process_all_unprocessed(
            analyzer=analyzer,
            cv_analyzer=cv_analyzer,
            questions_analyzer=questions_analyzer
        )

        logger.info(f"✅ Processing completed: {stats}")

        return ProcessSheetsResponse(
            success=True,
            message=f"Processed {stats['processed']} out of {stats['found']} interviews",
            stats=stats
        )

    except Exception as e:
        logger.error(f"❌ Error processing sheets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unprocessed", response_model=UnprocessedInterviewsResponse)
async def get_unprocessed_interviews():
    """
    Получить список необработанных интервью из Google Sheets

    Returns:
        Список необработанных интервью с основной информацией
    """
    try:
        from ..services.google_sheets_integration import get_sheets_integration

        sheets_service = get_sheets_integration()

        unprocessed = await sheets_service.scan_for_unprocessed_interviews()

        return UnprocessedInterviewsResponse(
            success=True,
            count=len(unprocessed),
            interviews=unprocessed
        )

    except Exception as e:
        logger.error(f"❌ Error getting unprocessed interviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload-prompts")
async def reload_prompts():
    """
    Перезагрузить промпты из prompts.yaml без перезапуска сервера

    Полезно для быстрого обновления промптов в production
    """
    try:
        from ..config.prompts_loader import reload_prompts

        reload_prompts()

        return {
            "success": True,
            "message": "Prompts reloaded successfully"
        }

    except Exception as e:
        logger.error(f"❌ Error reloading prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
