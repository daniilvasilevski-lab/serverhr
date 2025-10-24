"""
Database models for Interview Analyzer
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from .database import Base


class Candidate(Base):
    """Модель кандидата"""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    preferences = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Candidate(id={self.candidate_id}, name={self.name})>"


class Interview(Base):
    """Модель интервью"""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    video_url = Column(Text, nullable=False)
    cv_url = Column(Text)
    questions_url = Column(Text)

    interview_date = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)  # Длительность в секундах

    # Статус обработки
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))

    # Язык интервью
    language = Column(String(10), default="ru")  # ru, en, pl

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    candidate = relationship("Candidate", back_populates="interviews")
    analysis_result = relationship("AnalysisResult", back_populates="interview", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Interview(id={self.id}, candidate_id={self.candidate_id}, status={self.processing_status})>"


class AnalysisResult(Base):
    """Модель результатов анализа интервью"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), unique=True, nullable=False)

    # Общие оценки
    total_score = Column(Integer)  # Сумма всех баллов (0-100)
    weighted_score = Column(Float)  # Взвешенная оценка

    # Оценки по критериям (1-10)
    communication_skills = Column(Integer)
    motivation_learning = Column(Integer)
    professional_skills = Column(Integer)
    analytical_thinking = Column(Integer)
    unconventional_thinking = Column(Integer)
    teamwork_ability = Column(Integer)
    stress_resistance = Column(Integer)
    adaptability = Column(Integer)
    creativity_innovation = Column(Integer)
    overall_impression = Column(Integer)

    # Технические метрики
    audio_quality = Column(Integer)
    video_quality = Column(Integer)

    # Невербальные метрики
    eye_contact_percentage = Column(Float)
    gesture_frequency = Column(Integer)
    posture_confidence = Column(Integer)

    # Вербальные метрики
    speech_pace = Column(String(50))  # медленный, нормальный, быстрый
    vocabulary_richness = Column(Integer)
    grammar_quality = Column(Integer)
    answer_structure = Column(Integer)

    # Эмоциональный анализ (JSON)
    emotion_analysis = Column(JSON)

    # Рекомендация и обратная связь
    recommendation = Column(Text)
    detailed_feedback = Column(Text)

    # Детализированные оценки (JSON)
    detailed_scores = Column(JSON)

    # Метаданные анализа
    ai_model_version = Column(String(50))
    analysis_timestamp = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    interview = relationship("Interview", back_populates="analysis_result")

    def __repr__(self):
        return f"<AnalysisResult(interview_id={self.interview_id}, total_score={self.total_score})>"


class ProcessingLog(Base):
    """Логи обработки интервью"""
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))

    log_level = Column(String(20))  # INFO, WARNING, ERROR
    message = Column(Text)
    details = Column(JSON)  # Дополнительные детали в JSON

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ProcessingLog(interview_id={self.interview_id}, level={self.log_level})>"


class TaskSchedulerLog(Base):
    """Логи планировщика задач"""
    __tablename__ = "task_scheduler_logs"

    id = Column(Integer, primary_key=True, index=True)

    scan_started_at = Column(DateTime(timezone=True))
    scan_completed_at = Column(DateTime(timezone=True))

    interviews_found = Column(Integer, default=0)
    interviews_processed = Column(Integer, default=0)
    interviews_failed = Column(Integer, default=0)

    status = Column(String(50))  # running, completed, failed
    error_message = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TaskSchedulerLog(id={self.id}, status={self.status}, processed={self.interviews_processed})>"


class APIUsageLog(Base):
    """Логи использования API"""
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)

    endpoint = Column(String(255), index=True)  # /analyze, /analyze-temporal, etc.
    method = Column(String(10))  # GET, POST, etc.

    candidate_id = Column(String(100), index=True)

    request_timestamp = Column(DateTime(timezone=True), index=True)
    response_timestamp = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)  # Время обработки в миллисекундах

    status_code = Column(Integer)  # HTTP status code
    success = Column(Boolean)

    error_message = Column(Text)

    # IP и User Agent для безопасности
    client_ip = Column(String(50))
    user_agent = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<APIUsageLog(endpoint={self.endpoint}, status={self.status_code})>"
