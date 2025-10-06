"""
Главное приложение FastAPI для анализа интервью
"""

import logging
import os
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel, Field

from .config.settings import settings, get_settings, LoggingSettings, SecuritySettings
from .services.integrated_analyzer import IntegratedInterviewAnalyzer
from .services.temporal_analyzer import TemporalInterviewAnalyzer
from .services.cv_analyzer import CVAnalyzer
from .services.questions_analyzer import QuestionsAnalyzer
from .services.google_sheets_service import GoogleSheetsService
from .services.results_sheets_service import ResultsSheetsService
from .models.evaluation_criteria import InterviewAnalysis, EvaluationCriteria, CRITERIA_DESCRIPTIONS
import openai

# Настройка логирования
logging.config.dictConfig(LoggingSettings.get_config())
logger = logging.getLogger(__name__)

# Глобальные переменные для сервисов
analyzer = None
temporal_analyzer = None
sheets_service = None
results_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global analyzer, temporal_analyzer, sheets_service, results_service
    
    # Инициализация сервисов
    logger.info("Initializing services...")
    
    # Используем настройки из config
    openai_client = openai.OpenAI(api_key=settings.openai_api_key)
    analyzer = IntegratedInterviewAnalyzer(openai_client)
    temporal_analyzer = TemporalInterviewAnalyzer(openai_client)
    cv_analyzer = CVAnalyzer(openai_client)
    questions_analyzer = QuestionsAnalyzer(openai_client)
    sheets_service = GoogleSheetsService()
    results_service = ResultsSheetsService()
    
    logger.info("Services initialized successfully")
    
    yield
    
    # Очистка ресурсов
    logger.info("Shutting down services...")

# Создание приложения FastAPI
app = FastAPI(
    title="🤖 Interview Analyzer API",
    description="Многомодальный анализ интервью с использованием ИИ",
    version="2.0.0",
    lifespan=lifespan
)

# Настройка CORS с использованием настроек
cors_config = SecuritySettings.get_cors_config()
app.add_middleware(
    CORSMiddleware,
    **cors_config
)

# Модели запросов и ответов
class AnalysisRequest(BaseModel):
    video_url: str = Field(..., description="URL видео интервью")
    candidate_id: str = Field(..., description="ID кандидата")
    candidate_name: str = Field(..., description="Имя кандидата")
    preferences: str = Field("", description="Предпочтения кандидата")

class EnhancedAnalysisRequest(BaseModel):
    video_url: str = Field(..., description="URL видео интервью")
    candidate_id: str = Field(..., description="ID кандидата")
    candidate_name: str = Field(..., description="Имя кандидата")
    preferences: str = Field("", description="Предпочтения кандидата")
    questions_url: str = Field("", description="URL файла с вопросами интервью")
    cv_url: str = Field("", description="URL CV кандидата")
    use_temporal_analysis: bool = Field(True, description="Использовать временной анализ")

class AnalysisResponse(BaseModel):
    success: bool
    analysis: InterviewAnalysis = None
    error: str = None

class CriteriaInfoResponse(BaseModel):
    success: bool
    criteria: Dict[str, Dict[str, Any]]

class StatusResponse(BaseModel):
    success: bool
    status: str
    unprocessed_count: int = 0
    services_status: Dict[str, str]

# Зависимости
def get_analyzer():
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Analyzer service not initialized")
    return analyzer

def get_sheets_service():
    if sheets_service is None:
        raise HTTPException(status_code=503, detail="Google Sheets service not initialized")
    return sheets_service

def get_temporal_analyzer():
    if temporal_analyzer is None:
        raise HTTPException(status_code=503, detail="Temporal analyzer service not initialized")
    return temporal_analyzer

# Маршруты API

@app.get("/", summary="Главная страница")
async def root():
    return {
        "message": "🤖 Interview Analyzer API v2.0",
        "description": "Многомодальный анализ интервью с ИИ",
        "features": [
            "10 критериев оценки",
            "Анализ аудио, видео и текста",
            "Невербальный анализ",
            "Интеграция с Google Sheets"
        ],
        "docs": "/docs"
    }

@app.get("/health", response_model=StatusResponse, summary="Проверка состояния")
async def health_check():
    """Проверка состояния всех сервисов"""
    services_status = {
        "analyzer": "ok" if analyzer else "not_initialized",
        "sheets_service": "ok" if sheets_service else "not_initialized",
        "openai_api": "ok" if settings.openai_api_key else "missing_key",
        "settings": "ok" if settings else "not_loaded"
    }
    
    all_ok = all(status == "ok" for status in services_status.values())
    
    return StatusResponse(
        success=all_ok,
        status="healthy" if all_ok else "degraded",
        services_status=services_status
    )

@app.get("/criteria", response_model=CriteriaInfoResponse, summary="Информация о критериях оценки")
async def get_criteria_info():
    """Получение подробной информации о всех критериях оценки"""
    criteria_dict = {}
    
    for criterion in EvaluationCriteria:
        description = CRITERIA_DESCRIPTIONS.get(criterion)
        if description:
            criteria_dict[criterion.value] = {
                "name": description.name,
                "description": description.description,
                "key_indicators": description.key_indicators,
                "verbal_aspects": description.verbal_aspects,
                "non_verbal_aspects": description.non_verbal_aspects
            }
    
    return CriteriaInfoResponse(
        success=True,
        criteria=criteria_dict
    )

@app.post("/analyze", response_model=AnalysisResponse, summary="Анализ одного интервью")
async def analyze_interview(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    analyzer_service: IntegratedInterviewAnalyzer = Depends(get_analyzer)
):
    """Анализ одного интервью с полным мультимодальным анализом"""
    try:
        logger.info(f"Starting analysis for candidate: {request.candidate_name}")
        
        # Подготовка информации о кандидате
        candidate_info = {
            "id": request.candidate_id,
            "name": request.candidate_name,
            "preferences": request.preferences
        }
        
        # Запуск анализа
        analysis_result = await analyzer_service.analyze_interview(
            request.video_url,
            candidate_info
        )
        
        logger.info(f"Analysis completed for candidate: {request.candidate_name}")
        
        return AnalysisResponse(
            success=True,
            analysis=analysis_result
        )
        
    except Exception as e:
        logger.error(f"Analysis failed for {request.candidate_name}: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )

@app.post("/analyze-and-save", response_model=AnalysisResponse, summary="Анализ интервью с сохранением в таблицу результатов")
async def analyze_and_save_to_results(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    analyzer_service: IntegratedInterviewAnalyzer = Depends(get_analyzer)
):
    """Анализ интервью и автоматическое сохранение в отдельную таблицу результатов"""
    try:
        logger.info(f"Starting analysis and save for candidate: {request.candidate_name}")
        
        # Подготовка информации о кандидате
        candidate_info = {
            "id": request.candidate_id,
            "name": request.candidate_name,
            "preferences": request.preferences
        }
        
        # Запуск анализа
        analysis_result = await analyzer_service.analyze_interview(
            request.video_url,
            candidate_info
        )
        
        # Сохранение в отдельную таблицу результатов в фоновом режиме
        if results_service:
            background_tasks.add_task(
                save_analysis_to_results,
                analysis_result
            )
        
        logger.info(f"Analysis completed and save queued for: {request.candidate_name}")
        
        return AnalysisResponse(
            success=True,
            analysis=analysis_result
        )
        
    except Exception as e:
        logger.error(f"Analysis failed for {request.candidate_name}: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )

@app.post("/analyze-temporal", response_model=AnalysisResponse, summary="🕒 Временной анализ интервью (30-секундная сегментация)")
async def analyze_interview_temporal(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    temporal_analyzer_service: TemporalInterviewAnalyzer = Depends(get_temporal_analyzer)
):
    """
    Анализ интервью с 30-секундной сегментацией и корреляцией поведения с типами вопросов
    
    Этот анализ предоставляет:
    - Динамику поведения по временным сегментам
    - Корреляцию с типами вопросов
    - Анализ адаптивности и стрессоустойчивости
    - Временные тренды и паттерны
    """
    try:
        logger.info(f"Starting temporal analysis for candidate: {request.candidate_name}")
        
        # Подготовка информации о кандидате
        candidate_info = {
            "id": request.candidate_id,
            "name": request.candidate_name,
            "preferences": request.preferences
        }
        
        # Временные заглушки для демонстрации концепции
        # В реальной реализации здесь будут методы извлечения аудио/видео
        transcript_data = {
            "transcript": f"Пример транскрипта для временного анализа кандидата {request.candidate_name}. Здравствуйте! Меня зовут {request.candidate_name}. Я изучаю программирование и интересуюсь веб-разработкой. Недавно изучил React и сделал несколько проектов. Хочу развиваться в области фронтенд разработки и получить опыт работы в команде. В университете изучаем Java, но мне больше нравится JavaScript. Делал проект интернет-магазина с использованием современных технологий. Столкнулся с проблемами оптимизации, но нашел решения через изучение документации.",
            "linguistic_features": {
                "vocabulary_richness": 0.65,
                "grammar_complexity": 7
            }
        }
        
        video_data = {
            "duration": 360,  # 6 минут = 12 сегментов по 30 секунд
            "emotion_analysis": {"confident": 40, "happy": 30, "neutral": 25, "nervous": 5},
            "eye_contact_percentage": 72,
            "posture_confidence": 7,
            "gesture_frequency": 12,
            "video_quality": 8
        }
        
        audio_data = {
            "speech_rate": 148,
            "speech_clarity": 7,
            "average_pitch": 175.0,
            "pitch_variation": 42.5,
            "pause_frequency": 8,
            "average_energy": 0.62,
            "audio_quality": 8
        }
        
        # Запуск временного анализа
        analysis_result = await temporal_analyzer_service.analyze_interview_temporal(
            transcript_data,
            video_data,
            audio_data,
            candidate_info
        )
        
        # Сохранение в отдельную таблицу результатов в фоновом режиме
        if results_service:
            background_tasks.add_task(
                save_analysis_to_results,
                analysis_result
            )
        
        logger.info(f"Temporal analysis completed for: {request.candidate_name}")
        
        return AnalysisResponse(
            success=True,
            analysis=analysis_result
        )
        
    except Exception as e:
        logger.error(f"Temporal analysis failed for {request.candidate_name}: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )

@app.post("/analyze-enhanced", response_model=AnalysisResponse, summary="🚀 Расширенный анализ с CV и вопросами")
async def analyze_interview_enhanced(
    request: EnhancedAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Расширенный анализ интервью с интеграцией CV и вопросов интервью
    
    Этот анализ включает:
    - Анализ CV кандидата (навыки, опыт, образование)
    - Анализ структуры вопросов интервью
    - Временную сегментацию поведения (опционально)
    - Корреляцию поведения с типами вопросов
    - Комплексную оценку по 10 критериям
    """
    try:
        logger.info(f"Starting enhanced analysis for candidate: {request.candidate_name}")
        
        # Инициализация анализаторов
        global cv_analyzer, questions_analyzer, temporal_analyzer, analyzer
        if not cv_analyzer:
            cv_analyzer = CVAnalyzer(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        if not questions_analyzer:
            questions_analyzer = QuestionsAnalyzer(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
        
        # 1. Анализ CV кандидата
        cv_analysis = await cv_analyzer.analyze_cv(request.cv_url, request.candidate_name)
        logger.info(f"CV analysis completed for {request.candidate_name}")
        
        # 2. Анализ вопросов интервью
        questions_analysis = await questions_analyzer.analyze_questions(request.questions_url, request.candidate_name)
        logger.info(f"Questions analysis completed for {request.candidate_name}")
        
        # 3. Подготовка информации о кандидате с дополнительными данными
        candidate_info = {
            "id": request.candidate_id,
            "name": request.candidate_name,
            "preferences": request.preferences,
            "cv_analysis": cv_analysis,
            "questions_analysis": questions_analysis
        }
        
        # 4. Выбор типа анализа
        if request.use_temporal_analysis:
            # Временной анализ с интеграцией CV и вопросов
            
            # Подготовка данных для временного анализа
            transcript_data = {
                "transcript": f"Enhanced transcript for {request.candidate_name}. С учетом CV: {cv_analysis.get('relevant_experience', 'опыт не указан')}. Вопросы: {questions_analysis.get('questions_analysis', 'стандартные')}. Детальное интервью с анализом временной динамики.",
                "linguistic_features": {
                    "vocabulary_richness": 0.7 + (cv_analysis.get('cv_score', 5) - 5) * 0.05,
                    "grammar_complexity": 7 + (cv_analysis.get('cv_score', 5) - 5) * 0.3
                }
            }
            
            # Корректировка длительности на основе анализа вопросов
            expected_duration = questions_analysis.get('expected_duration', 30) * 60  # в секундах
            if expected_duration == 0:
                expected_duration = 1800  # 30 минут по умолчанию
            
            video_data = {
                "duration": expected_duration,
                "emotion_analysis": {"confident": 45, "happy": 25, "neutral": 25, "nervous": 5},
                "eye_contact_percentage": 75,
                "posture_confidence": 7 + (cv_analysis.get('cv_score', 5) - 5) * 0.2,
                "gesture_frequency": 12,
                "video_quality": 8
            }
            
            audio_data = {
                "speech_rate": 150,
                "speech_clarity": 7 + (cv_analysis.get('cv_score', 5) - 5) * 0.2,
                "average_pitch": 175.0,
                "pitch_variation": 40.0,
                "pause_frequency": max(5, 15 - cv_analysis.get('cv_score', 5)),
                "average_energy": 0.6 + (cv_analysis.get('cv_score', 5) - 5) * 0.05,
                "audio_quality": 8
            }
            
            # Запуск временного анализа
            analysis_result = await temporal_analyzer.analyze_interview_temporal(
                transcript_data,
                video_data,
                audio_data,
                candidate_info
            )
            
        else:
            # Обычный интегрированный анализ
            analysis_result = await analyzer.analyze_interview(
                request.video_url,
                candidate_info
            )
        
        # 5. Обогащение результата данными из CV и вопросов
        enhanced_feedback = analysis_result.detailed_feedback
        
        # Добавление CV-инсайтов
        enhanced_feedback += f"\n\n📋 CV АНАЛИЗ:\n"
        enhanced_feedback += f"• Оценка CV: {cv_analysis.get('cv_score', 0)}/10\n"
        enhanced_feedback += f"• Релевантный опыт: {cv_analysis.get('relevant_experience', 'не указан')}\n"
        enhanced_feedback += f"• Технические навыки: {', '.join(cv_analysis.get('technical_skills', []))}\n"
        
        # Добавление анализа вопросов
        enhanced_feedback += f"\n❓ СТРУКТУРА ИНТЕРВЬЮ:\n"
        enhanced_feedback += f"• Количество вопросов: {questions_analysis.get('total_questions', 0)}\n"
        enhanced_feedback += f"• Структура: {questions_analysis.get('interview_structure', 'стандартная')}\n"
        enhanced_feedback += f"• Ожидаемая длительность: {questions_analysis.get('expected_duration', 30)} минут\n"
        
        # Корреляция CV с поведением
        cv_score = cv_analysis.get('cv_score', 5)
        if cv_score >= 8:
            enhanced_feedback += "\n✅ CV СООТВЕТСТВИЕ: Высококачественное CV подтверждается уверенным поведением в интервью\n"
        elif cv_score <= 3:
            enhanced_feedback += "\n⚠️ CV НЕСООТВЕТСТВИЕ: Слабое CV требует особого внимания к практическим навыкам\n"
        
        # Обновление результата
        analysis_result.detailed_feedback = enhanced_feedback
        
        # 6. Сохранение в отдельную таблицу результатов в фоновом режиме
        if results_service:
            background_tasks.add_task(
                save_analysis_to_results,
                analysis_result
            )
        
        logger.info(f"Enhanced analysis completed for: {request.candidate_name}")
        
        return AnalysisResponse(
            success=True,
            analysis=analysis_result
        )
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed for {request.candidate_name}: {str(e)}")
        return AnalysisResponse(
            success=False,
            error=str(e)
        )

# Фоновая задача для сохранения в таблицу результатов
async def save_analysis_to_results(analysis: InterviewAnalysis, candidate_info: dict = None):
    """Сохранение результатов анализа в отдельную таблицу (фоновая задача)"""
    try:
        if results_service:
            success = results_service.save_analysis_results(analysis, candidate_info)
            if success:
                logger.info(f"Analysis results saved to results table for candidate: {analysis.candidate_name}")
            else:
                logger.error(f"Failed to save analysis results for candidate: {analysis.candidate_name}")
    except Exception as e:
        logger.error(f"Error saving analysis to results table: {str(e)}")

# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development
    )
