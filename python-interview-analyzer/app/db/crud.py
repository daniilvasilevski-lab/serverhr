"""
CRUD operations for database models
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .models import Candidate, Interview, AnalysisResult, ProcessingLog, APIUsageLog


class CandidateCRUD:
    """CRUD операции для кандидатов"""

    @staticmethod
    def create(db: Session, candidate_id: str, name: str, email: str = None, phone: str = None, preferences: str = None) -> Candidate:
        """Создание нового кандидата"""
        candidate = Candidate(
            candidate_id=candidate_id,
            name=name,
            email=email,
            phone=phone,
            preferences=preferences
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return candidate

    @staticmethod
    def get_by_id(db: Session, candidate_id: str) -> Optional[Candidate]:
        """Получение кандидата по ID"""
        return db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()

    @staticmethod
    def get_or_create(db: Session, candidate_id: str, name: str, **kwargs) -> Candidate:
        """Получение существующего или создание нового кандидата"""
        candidate = CandidateCRUD.get_by_id(db, candidate_id)
        if candidate:
            # Обновление данных если изменились
            if kwargs.get('email'):
                candidate.email = kwargs['email']
            if kwargs.get('phone'):
                candidate.phone = kwargs['phone']
            if kwargs.get('preferences'):
                candidate.preferences = kwargs['preferences']
            db.commit()
            db.refresh(candidate)
        else:
            candidate = CandidateCRUD.create(db, candidate_id, name, **kwargs)
        return candidate

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Candidate]:
        """Получение всех кандидатов"""
        return db.query(Candidate).offset(skip).limit(limit).all()

    @staticmethod
    def search_by_name(db: Session, name: str) -> List[Candidate]:
        """Поиск кандидатов по имени"""
        return db.query(Candidate).filter(Candidate.name.ilike(f"%{name}%")).all()


class InterviewCRUD:
    """CRUD операции для интервью"""

    @staticmethod
    def create(db: Session, candidate_id: int, video_url: str, cv_url: str = None, questions_url: str = None, language: str = "ru") -> Interview:
        """Создание нового интервью"""
        interview = Interview(
            candidate_id=candidate_id,
            video_url=video_url,
            cv_url=cv_url,
            questions_url=questions_url,
            language=language,
            processing_status="pending",
            interview_date=datetime.now()
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)
        return interview

    @staticmethod
    def get_by_id(db: Session, interview_id: int) -> Optional[Interview]:
        """Получение интервью по ID"""
        return db.query(Interview).filter(Interview.id == interview_id).first()

    @staticmethod
    def get_pending(db: Session, limit: int = 10) -> List[Interview]:
        """Получение необработанных интервью"""
        return db.query(Interview).filter(
            Interview.processing_status == "pending"
        ).limit(limit).all()

    @staticmethod
    def update_status(db: Session, interview_id: int, status: str) -> Optional[Interview]:
        """Обновление статуса обработки"""
        interview = InterviewCRUD.get_by_id(db, interview_id)
        if interview:
            interview.processing_status = status
            if status == "processing":
                interview.processing_started_at = datetime.now()
            elif status in ["completed", "failed"]:
                interview.processing_completed_at = datetime.now()
            db.commit()
            db.refresh(interview)
        return interview

    @staticmethod
    def get_by_candidate(db: Session, candidate_id: int) -> List[Interview]:
        """Получение всех интервью кандидата"""
        return db.query(Interview).filter(Interview.candidate_id == candidate_id).all()


class AnalysisResultCRUD:
    """CRUD операции для результатов анализа"""

    @staticmethod
    def create_from_analysis(db: Session, interview_id: int, analysis_data: dict) -> AnalysisResult:
        """Создание результата анализа из объекта InterviewAnalysis"""

        # Извлечение оценок по критериям
        scores = analysis_data.get('scores', {})

        result = AnalysisResult(
            interview_id=interview_id,
            total_score=analysis_data.get('total_score', 0),
            weighted_score=analysis_data.get('weighted_score', 0.0),

            # Оценки по критериям
            communication_skills=scores.get('communication_skills', {}).get('score', 0),
            motivation_learning=scores.get('motivation_learning', {}).get('score', 0),
            professional_skills=scores.get('professional_skills', {}).get('score', 0),
            analytical_thinking=scores.get('analytical_thinking', {}).get('score', 0),
            unconventional_thinking=scores.get('unconventional_thinking', {}).get('score', 0),
            teamwork_ability=scores.get('teamwork_ability', {}).get('score', 0),
            stress_resistance=scores.get('stress_resistance', {}).get('score', 0),
            adaptability=scores.get('adaptability', {}).get('score', 0),
            creativity_innovation=scores.get('creativity_innovation', {}).get('score', 0),
            overall_impression=scores.get('overall_impression', {}).get('score', 0),

            # Технические метрики
            audio_quality=analysis_data.get('audio_quality', 0),
            video_quality=analysis_data.get('video_quality', 0),

            # Невербальные метрики
            eye_contact_percentage=analysis_data.get('eye_contact_percentage', 0.0),
            gesture_frequency=analysis_data.get('gesture_frequency', 0),
            posture_confidence=analysis_data.get('posture_confidence', 0),

            # Вербальные метрики
            speech_pace=analysis_data.get('speech_pace', ''),
            vocabulary_richness=analysis_data.get('vocabulary_richness', 0),
            grammar_quality=analysis_data.get('grammar_quality', 0),
            answer_structure=analysis_data.get('answer_structure', 0),

            # Эмоциональный анализ
            emotion_analysis=analysis_data.get('emotion_analysis', {}),

            # Рекомендация и обратная связь
            recommendation=analysis_data.get('recommendation', ''),
            detailed_feedback=analysis_data.get('detailed_feedback', ''),

            # Детализированные оценки
            detailed_scores=scores,

            # Метаданные
            ai_model_version=analysis_data.get('ai_model_version', ''),
            analysis_timestamp=datetime.fromisoformat(analysis_data.get('analysis_timestamp', datetime.now().isoformat()))
        )

        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def get_by_interview_id(db: Session, interview_id: int) -> Optional[AnalysisResult]:
        """Получение результата анализа для интервью"""
        return db.query(AnalysisResult).filter(AnalysisResult.interview_id == interview_id).first()

    @staticmethod
    def get_top_candidates(db: Session, limit: int = 10) -> List[AnalysisResult]:
        """Получение лучших кандидатов по оценке"""
        return db.query(AnalysisResult).order_by(
            AnalysisResult.weighted_score.desc()
        ).limit(limit).all()

    @staticmethod
    def get_by_score_range(db: Session, min_score: int, max_score: int) -> List[AnalysisResult]:
        """Получение результатов в диапазоне оценок"""
        return db.query(AnalysisResult).filter(
            AnalysisResult.total_score >= min_score,
            AnalysisResult.total_score <= max_score
        ).all()


class ProcessingLogCRUD:
    """CRUD операции для логов обработки"""

    @staticmethod
    def create(db: Session, interview_id: int, log_level: str, message: str, details: dict = None):
        """Создание лога обработки"""
        log = ProcessingLog(
            interview_id=interview_id,
            log_level=log_level,
            message=message,
            details=details or {}
        )
        db.add(log)
        db.commit()
        return log

    @staticmethod
    def get_by_interview(db: Session, interview_id: int) -> List[ProcessingLog]:
        """Получение всех логов для интервью"""
        return db.query(ProcessingLog).filter(
            ProcessingLog.interview_id == interview_id
        ).order_by(ProcessingLog.created_at.desc()).all()


class APIUsageLogCRUD:
    """CRUD операции для логов использования API"""

    @staticmethod
    def create(db: Session, endpoint: str, method: str, candidate_id: str = None,
               duration_ms: int = 0, status_code: int = 200, success: bool = True,
               error_message: str = None, client_ip: str = None, user_agent: str = None):
        """Создание лога использования API"""
        log = APIUsageLog(
            endpoint=endpoint,
            method=method,
            candidate_id=candidate_id,
            request_timestamp=datetime.now(),
            response_timestamp=datetime.now(),
            duration_ms=duration_ms,
            status_code=status_code,
            success=success,
            error_message=error_message,
            client_ip=client_ip,
            user_agent=user_agent
        )
        db.add(log)
        db.commit()
        return log

    @staticmethod
    def get_stats_by_endpoint(db: Session, start_date: datetime = None, end_date: datetime = None):
        """Получение статистики по эндпоинтам"""
        query = db.query(
            APIUsageLog.endpoint,
            db.func.count(APIUsageLog.id).label('total_requests'),
            db.func.avg(APIUsageLog.duration_ms).label('avg_duration_ms'),
            db.func.sum(db.case([(APIUsageLog.success == True, 1)], else_=0)).label('successful_requests'),
            db.func.sum(db.case([(APIUsageLog.success == False, 1)], else_=0)).label('failed_requests')
        ).group_by(APIUsageLog.endpoint)

        if start_date:
            query = query.filter(APIUsageLog.request_timestamp >= start_date)
        if end_date:
            query = query.filter(APIUsageLog.request_timestamp <= end_date)

        return query.all()
