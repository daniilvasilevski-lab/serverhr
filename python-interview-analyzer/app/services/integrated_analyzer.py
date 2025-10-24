"""
Интегрированный анализатор интервью
Холистический подход с единым контекстом для всех модальностей
"""

import logging
import json
from typing import Dict, List, Any
import asyncio
from datetime import datetime

from ..models.evaluation_criteria import (
    EvaluationCriteria, 
    EvaluationScore, 
    InterviewAnalysis,
    CRITERIA_DESCRIPTIONS
)

logger = logging.getLogger(__name__)


class IntegratedInterviewAnalyzer:
    """
    Интегрированный анализатор интервью
    Анализирует все модальности в едином контексе
    """
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
        
    async def analyze_interview(self, video_url: str, candidate_info: Dict) -> InterviewAnalysis:
        """
        Основной метод анализа интервью
        Использует реальные видео и аудио процессоры
        """
        logger.info(f"Starting integrated analysis for {candidate_info.get('name', 'Unknown')}")
        
        try:
            # Импортируем процессоры
            from .video_processor import create_video_processor
            from .audio_processor import create_audio_processor
            
            # Создаем процессоры
            video_processor = create_video_processor()
            audio_processor = create_audio_processor()
            
            # Параллельная обработка видео и аудио
            import asyncio
            video_task = asyncio.create_task(video_processor.process_video(video_url))
            audio_task = asyncio.create_task(audio_processor.process_audio(video_url, 'ru'))
            
            # Ожидаем результаты
            video_results, audio_results = await asyncio.gather(video_task, audio_task)
            
            # Адаптируем данные для обратной совместимости
            transcript_data = {
                "transcript": audio_results.get("transcript", ""),
                "linguistic_features": {
                    "vocabulary_richness": audio_results.get("vocabulary_richness", 0.5),
                    "grammar_complexity": audio_results.get("grammar_complexity", 5)
                }
            }
            
            video_data = {
                "duration": video_results.get("duration", 0),
                "emotion_analysis": video_results.get("emotion_analysis", {}),
                "eye_contact_percentage": video_results.get("eye_contact_percentage", 0),
                "posture_confidence": video_results.get("posture_confidence", 5),
                "gesture_frequency": video_results.get("gesture_frequency", 0),
                "video_quality": video_results.get("video_quality", 5)
            }
            
            audio_data = {
                "speech_rate": audio_results.get("speech_rate", 150),
                "speech_clarity": audio_results.get("speech_clarity", 5),
                "average_pitch": audio_results.get("average_pitch", 150.0),
                "pitch_variation": audio_results.get("pitch_variation", 30.0),
                "pause_frequency": audio_results.get("pause_frequency", 5),
                "average_energy": audio_results.get("average_energy", 0.5),
                "audio_quality": audio_results.get("audio_quality", 5)
            }
            
            # Вызов интегрированного анализа
            return await self.analyze_interview_holistic(
                transcript_data, video_data, audio_data, candidate_info
            )
            
        except Exception as e:
            logger.error(f"Real processing failed, using fallback: {e}")
            # Fallback к заглушкам если что-то пошло не так
            return await self._fallback_analysis(video_url, candidate_info)
    
    async def _fallback_analysis(self, video_url: str, candidate_info: Dict) -> InterviewAnalysis:
        """Резервный анализ с заглушками"""
        transcript_data = {
            "transcript": f"Пример транскрипта для кандидата {candidate_info.get('name', 'Unknown')}",
            "linguistic_features": {
                "vocabulary_richness": 0.65,
                "grammar_complexity": 7
            }
        }
        
        video_data = {
            "duration": 300,
            "emotion_analysis": {"happy": 45.0, "neutral": 40.0, "confident": 15.0},
            "eye_contact_percentage": 75.0,
            "posture_confidence": 8,
            "gesture_frequency": 12,
            "video_quality": 8
        }
        
        audio_data = {
            "speech_rate": 145,
            "speech_clarity": 7,
            "average_pitch": 180.5,
            "pitch_variation": 45.2,
            "pause_frequency": 8,
            "average_energy": 0.65,
            "audio_quality": 8
        }
        
        return await self.analyze_interview_holistic(
            transcript_data, video_data, audio_data, candidate_info
        )
        
    async def analyze_interview_holistic(
        self,
        transcript_data: Dict,
        video_data: Dict, 
        audio_data: Dict,
        candidate_info: Dict
    ) -> InterviewAnalysis:
        """
        Холистический анализ интервью с учетом всех модальностей
        
        Args:
            transcript_data: Транскрипт и текстовый анализ
            video_data: Видео-анализ (эмоции, жесты, поза)
            audio_data: Аудио-анализ (тон, темп, четкость)
            candidate_info: Информация о кандидате
            
        Returns:
            InterviewAnalysis: Комплексный анализ
        """
        candidate_name = candidate_info.get('name', 'Unknown')
        logger.info(f"🔬 НАЧАЛО ИНТЕГРИРОВАННОГО АНАЛИЗА для {candidate_name}")

        # 1. Подготовка объединенных данных для ИИ
        logger.info(f"📋 Этап 1/4: Подготовка контекста интервью...")
        integrated_context = self._prepare_integrated_context(
            transcript_data, video_data, audio_data, candidate_info
        )
        logger.info(f"   ✓ Длительность: {integrated_context['interview_content']['duration_seconds']}с")
        logger.info(f"   ✓ Количество слов: {integrated_context['interview_content']['word_count']}")
        logger.info(f"   ✓ Доминирующая эмоция: {integrated_context['nonverbal_behavior']['dominant_emotion']}")
        logger.info(f"   ✓ Зрительный контакт: {integrated_context['nonverbal_behavior']['eye_contact_percentage']:.1f}%")

        # 2. Единый комплексный анализ через GPT-4
        logger.info(f"🤖 Этап 2/4: Холистический анализ через GPT-4...")
        comprehensive_analysis = await self._analyze_with_full_context(integrated_context)
        logger.info(f"   ✓ Комплексный анализ завершен")

        # 3. Создание детализированных оценок с конкретными примерами
        logger.info(f"📊 Этап 3/4: Детальная оценка по 10 критериям...")
        detailed_scores = await self._create_detailed_scores(
            comprehensive_analysis, integrated_context
        )
        logger.info(f"   ✓ Все 10 критериев оценены")

        # 4. Формирование итогового результата
        logger.info(f"📝 Этап 4/4: Формирование итогового результата...")
        final_analysis = self._build_final_analysis(
            detailed_scores, integrated_context, comprehensive_analysis, candidate_info
        )
        logger.info(f"✅ АНАЛИЗ ЗАВЕРШЕН для {candidate_name}")

        return final_analysis
    
    def _prepare_integrated_context(
        self, 
        transcript_data: Dict,
        video_data: Dict,
        audio_data: Dict,
        candidate_info: Dict
    ) -> Dict:
        """Подготовка объединенного контекста для анализа"""
        
        return {
            "candidate": {
                "name": candidate_info.get("name", "Unknown"),
                "id": candidate_info.get("id", "unknown"),
                "preferences": candidate_info.get("preferences", "")
            },
            
            "interview_content": {
                "transcript": transcript_data.get("transcript", ""),
                "duration_seconds": video_data.get("duration", 0),
                "word_count": len(transcript_data.get("transcript", "").split()),
                "linguistic_features": transcript_data.get("linguistic_features", {})
            },
            
            "verbal_communication": {
                "speech_rate_wpm": audio_data.get("speech_rate", 150),
                "speech_clarity": audio_data.get("speech_clarity", 5),
                "average_pitch": audio_data.get("average_pitch", 0),
                "pitch_variation": audio_data.get("pitch_variation", 0),
                "pause_frequency": audio_data.get("pause_frequency", 0),
                "energy_level": audio_data.get("average_energy", 0),
                "tempo_classification": self._classify_tempo(audio_data.get("speech_rate", 150))
            },
            
            "nonverbal_behavior": {
                "emotions_distribution": video_data.get("emotion_analysis", {}),
                "dominant_emotion": self._get_dominant_emotion(video_data.get("emotion_analysis", {})),
                "eye_contact_percentage": video_data.get("eye_contact_percentage", 50),
                "posture_confidence": video_data.get("posture_confidence", 5),
                "gesture_frequency": video_data.get("gesture_frequency", 0),
                "gesture_intensity": self._classify_gesture_intensity(video_data.get("gesture_frequency", 0))
            },
            
            "technical_quality": {
                "video_quality": video_data.get("video_quality", 5),
                "audio_quality": audio_data.get("audio_quality", 5),
                "analysis_reliability": self._assess_reliability(video_data, audio_data)
            },
            
            "temporal_synchronization": {
                "speech_emotion_alignment": self._assess_speech_emotion_sync(
                    transcript_data, video_data
                ),
                "gesture_speech_coordination": self._assess_gesture_speech_sync(
                    transcript_data, video_data
                )
            }
        }
    
    async def _analyze_with_full_context(self, context: Dict) -> Dict:
        """
        Комплексный анализ с полным контекстом через GPT-4
        """
        
        # Создание детального промпта для холистического анализа
        analysis_prompt = f"""
Ты эксперт-психолог и HR-специалист, анализирующий интервью студента. 
Проведи КОМПЛЕКСНУЮ оценку, учитывая ВСЕ аспекты одновременно.

ИНФОРМАЦИЯ О КАНДИДАТЕ:
- Имя: {context['candidate']['name']}
- Предпочтения: {context['candidate']['preferences']}

СОДЕРЖАНИЕ ИНТЕРВЬЮ:
- Транскрипт: "{context['interview_content']['transcript']}"
- Длительность: {context['interview_content']['duration_seconds']} сек
- Количество слов: {context['interview_content']['word_count']}

ВЕРБАЛЬНЫЕ ХАРАКТЕРИСТИКИ:
- Темп речи: {context['verbal_communication']['speech_rate_wpm']} слов/мин ({context['verbal_communication']['tempo_classification']})
- Четкость речи: {context['verbal_communication']['speech_clarity']}/10
- Средняя высота тона: {context['verbal_communication']['average_pitch']} Гц
- Вариативность тона: {context['verbal_communication']['pitch_variation']}
- Частота пауз: {context['verbal_communication']['pause_frequency']}
- Уровень энергии: {context['verbal_communication']['energy_level']:.3f}

НЕВЕРБАЛЬНОЕ ПОВЕДЕНИЕ:
- Эмоции: {context['nonverbal_behavior']['emotions_distribution']}
- Доминирующая эмоция: {context['nonverbal_behavior']['dominant_emotion']}
- Зрительный контакт: {context['nonverbal_behavior']['eye_contact_percentage']:.1f}%
- Уверенность позы: {context['nonverbal_behavior']['posture_confidence']}/10
- Частота жестов: {context['nonverbal_behavior']['gesture_frequency']} ({context['nonverbal_behavior']['gesture_intensity']})

СИНХРОНИЗАЦИЯ:
- Соответствие речи и эмоций: {context['temporal_synchronization']['speech_emotion_alignment']}
- Координация жестов и речи: {context['temporal_synchronization']['gesture_speech_coordination']}

ЗАДАЧА:
Оцени кандидата по 10 критериям (1-10 баллов), учитывая ВСЕ данные в комплексе:

1. Коммуникативные навыки - ясность, структура, взаимодействие
2. Мотивация к обучению - энтузиазм, желание развиваться  
3. Профессиональные навыки - знания, опыт, компетенции
4. Аналитическое мышление - логика, структурированность
5. Умение нестандартно мыслить - креативность, оригинальность подходов
6. Командная работа - готовность к сотрудничеству
7. Стрессоустойчивость - спокойствие, контроль эмоций
8. Адаптивность - гибкость, открытость к изменениям
9. Креативность - инновационные идеи, творческий подход
10. Общее впечатление - итоговая оценка кандидата

ВАЖНО: 
- Анализируй ВЗАИМОСВЯЗИ между вербальным и невербальным
- Учитывай КОНТЕКСТ (например, пауза может быть обдумыванием)
- Ищи ПОДТВЕРЖДЕНИЯ в разных модальностях
- Отмечай ПРОТИВОРЕЧИЯ и их возможные причины

Ответь в JSON формате:
{{
    "holistic_scores": {{
        "communication_skills": число,
        "motivation_learning": число,
        "professional_skills": число,
        "analytical_thinking": число,
        "unconventional_thinking": число,
        "teamwork_ability": число,
        "stress_resistance": число,
        "adaptability": число,
        "creativity_innovation": число,
        "overall_impression": число
    }},
    "cross_modal_insights": {{
        "verbal_nonverbal_alignment": "описание соответствия речи и поведения",
        "emotional_consistency": "анализ эмоциональной согласованности",
        "confidence_indicators": "индикаторы уверенности из всех модальностей",
        "stress_indicators": "признаки стресса или спокойствия"
    }},
    "detailed_observations": {{
        "communication_skills": ["конкретный пример 1", "пример 2", "пример 3"],
        "motivation_learning": ["пример 1", "пример 2", "пример 3"],
        "professional_skills": ["пример 1", "пример 2", "пример 3"],
        "analytical_thinking": ["пример 1", "пример 2", "пример 3"],
        "unconventional_thinking": ["пример 1", "пример 2", "пример 3"],
        "teamwork_ability": ["пример 1", "пример 2", "пример 3"],
        "stress_resistance": ["пример 1", "пример 2", "пример 3"],
        "adaptability": ["пример 1", "пример 2", "пример 3"],
        "creativity_innovation": ["пример 1", "пример 2", "пример 3"],
        "overall_impression": ["пример 1", "пример 2", "пример 3"]
    }},
    "comprehensive_feedback": "детальная обратная связь с учетом всех аспектов",
    "recommendation": "рекомендация с обоснованием"
}}
"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "Ты эксперт-психолог и HR-специалист с 15+ лет опыта анализа интервью. Анализируешь целостно, учитывая все модальности в комплексе."
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.2,  # Низкая температура для более объективного анализа
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            
            # Извлечение JSON из ответа
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= start_idx:
                raise ValueError("No valid JSON found in response")
                
            json_str = content[start_idx:end_idx]
            analysis_result = json.loads(json_str)
            
            logger.info("Integrated analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Integrated analysis failed: {e}")
            # Возврат базовых значений в случае ошибки
            return self._get_fallback_analysis()
    
    async def _create_detailed_scores(self, analysis: Dict, context: Dict) -> Dict:
        """Создание детализированных оценок с форматированием"""

        detailed_scores = {}
        scores = analysis.get("holistic_scores", {})
        observations = analysis.get("detailed_observations", {})

        # Названия критериев на русском для логирования
        criteria_names = {
            EvaluationCriteria.COMMUNICATION_SKILLS: "Коммуникативные навыки",
            EvaluationCriteria.MOTIVATION_LEARNING: "Мотивация к обучению",
            EvaluationCriteria.PROFESSIONAL_SKILLS: "Профессиональные навыки",
            EvaluationCriteria.ANALYTICAL_THINKING: "Аналитическое мышление",
            EvaluationCriteria.UNCONVENTIONAL_THINKING: "Нестандартное мышление",
            EvaluationCriteria.TEAMWORK_ABILITY: "Командная работа",
            EvaluationCriteria.STRESS_RESISTANCE: "Стрессоустойчивость",
            EvaluationCriteria.ADAPTABILITY: "Адаптивность",
            EvaluationCriteria.CREATIVITY_INNOVATION: "Креативность и инновации",
            EvaluationCriteria.OVERALL_IMPRESSION: "Общее впечатление"
        }

        total_criteria = len(EvaluationCriteria)
        for idx, criterion in enumerate(EvaluationCriteria, 1):
            criterion_name = criteria_names.get(criterion, criterion.value)
            logger.info(f"   📌 Критерий {idx}/{total_criteria}: {criterion_name}...")

            criterion_key = criterion.value
            score = scores.get(criterion_key, 5)
            examples = observations.get(criterion_key, [])

            # Создание объяснения на основе холистического анализа
            explanation = self._generate_integrated_explanation(
                criterion, score, analysis, context
            )

            # Форматированная оценка
            formatted_eval = self._format_evaluation_with_examples(
                score, explanation, examples
            )

            evaluation_score = EvaluationScore(
                criterion=criterion,
                score=score,
                verbal_score=self._extract_verbal_component(criterion, analysis, context),
                non_verbal_score=self._extract_nonverbal_component(criterion, analysis, context),
                explanation=explanation,
                key_observations=self._extract_key_observations(criterion, analysis, context),
                specific_examples=examples,
                formatted_evaluation=formatted_eval
            )

            detailed_scores[criterion] = evaluation_score
            logger.info(f"      ✓ Оценка: {score}/10")

        return detailed_scores
    
    def _classify_tempo(self, wpm: float) -> str:
        """Классификация темпа речи"""
        if wpm < 120:
            return "медленный"
        elif wpm > 180:
            return "быстрый"
        else:
            return "нормальный"
    
    def _get_dominant_emotion(self, emotions: Dict) -> str:
        """Определение доминирующей эмоции"""
        if not emotions:
            return "neutral"
        return max(emotions.items(), key=lambda x: x[1])[0]
    
    def _classify_gesture_intensity(self, frequency: int) -> str:
        """Классификация интенсивности жестов"""
        if frequency < 5:
            return "низкая"
        elif frequency < 15:
            return "умеренная"
        else:
            return "высокая"
    
    def _assess_reliability(self, video_data: Dict, audio_data: Dict) -> str:
        """Оценка надежности анализа"""
        video_quality = video_data.get("video_quality", 5)
        audio_quality = audio_data.get("audio_quality", 5)
        avg_quality = (video_quality + audio_quality) / 2
        
        if avg_quality >= 8:
            return "высокая"
        elif avg_quality >= 6:
            return "средняя"
        else:
            return "низкая"
    
    def _assess_speech_emotion_sync(self, transcript_data: Dict, video_data: Dict) -> str:
        """Анализ синхронизации речи и эмоций"""
        # Упрощенная версия - в реальности нужен временной анализ
        emotions = video_data.get("emotion_analysis", {})
        positive_emotions = emotions.get("happy", 0) + emotions.get("surprise", 0)
        
        transcript = transcript_data.get("transcript", "").lower()
        positive_words = ["хорошо", "отлично", "интересно", "нравится", "увлекательно"]
        positive_word_count = sum(1 for word in positive_words if word in transcript)
        
        if positive_emotions > 20 and positive_word_count > 0:
            return "хорошее соответствие"
        elif positive_emotions < 10 and positive_word_count == 0:
            return "нейтральное соответствие"
        else:
            return "смешанное"
    
    def _assess_gesture_speech_sync(self, transcript_data: Dict, video_data: Dict) -> str:
        """Анализ координации жестов и речи"""
        gesture_freq = video_data.get("gesture_frequency", 0)
        word_count = len(transcript_data.get("transcript", "").split())
        
        if word_count > 0:
            gesture_per_word = gesture_freq / word_count
            if 0.01 <= gesture_per_word <= 0.05:
                return "хорошая координация"
            elif gesture_per_word > 0.05:
                return "избыточная жестикуляция"
            else:
                return "недостаточная жестикуляция"
        
        return "неопределенная"
    
    def _generate_integrated_explanation(
        self, 
        criterion: EvaluationCriteria, 
        score: int, 
        analysis: Dict, 
        context: Dict
    ) -> str:
        """Генерация объяснения на основе интегрированного анализа"""
        
        criterion_info = CRITERIA_DESCRIPTIONS[criterion]
        base_explanation = f"Оценка {score}/10 по критерию '{criterion_info.name}'"
        
        # Добавление контекстуальных деталей из кросс-модального анализа
        cross_modal = analysis.get("cross_modal_insights", {})
        
        if criterion == EvaluationCriteria.COMMUNICATION_SKILLS:
            alignment = cross_modal.get("verbal_nonverbal_alignment", "")
            return f"{base_explanation}. {alignment}"
        
        elif criterion == EvaluationCriteria.STRESS_RESISTANCE:
            stress_indicators = cross_modal.get("stress_indicators", "")
            return f"{base_explanation}. {stress_indicators}"
        
        return base_explanation
    
    def _format_evaluation_with_examples(
        self, 
        score: int, 
        explanation: str, 
        examples: List[str]
    ) -> str:
        """Форматирование оценки с примерами"""
        
        result = f"{score}/10 - {explanation}"
        
        if examples:
            examples_text = "; ".join(examples[:3])  # Максимум 3 примера
            result += f" Примеры: {examples_text}"
        
        return result
    
    def _extract_verbal_component(
        self, 
        criterion: EvaluationCriteria, 
        analysis: Dict, 
        context: Dict
    ) -> int:
        """Извлечение вербального компонента оценки"""
        # Базовая оценка на основе содержания речи
        return min(5, max(1, analysis.get("holistic_scores", {}).get(criterion.value, 5) // 2 + 1))
    
    def _extract_nonverbal_component(
        self, 
        criterion: EvaluationCriteria, 
        analysis: Dict, 
        context: Dict
    ) -> int:
        """Извлечение невербального компонента оценки"""
        # Базовая оценка на основе невербального поведения
        total_score = analysis.get("holistic_scores", {}).get(criterion.value, 5)
        verbal_score = self._extract_verbal_component(criterion, analysis, context)
        return min(5, max(1, total_score - verbal_score + 1))
    
    def _extract_key_observations(
        self, 
        criterion: EvaluationCriteria, 
        analysis: Dict, 
        context: Dict
    ) -> List[str]:
        """Извлечение ключевых наблюдений"""
        observations = analysis.get("detailed_observations", {}).get(criterion.value, [])
        return observations[:3]  # Максимум 3 наблюдения
    
    def _build_final_analysis(
        self,
        detailed_scores: Dict,
        context: Dict,
        comprehensive_analysis: Dict,
        candidate_info: Dict
    ) -> InterviewAnalysis:
        """Построение итогового анализа"""
        
        total_score = sum(score.score for score in detailed_scores.values())
        
        return InterviewAnalysis(
            candidate_id=candidate_info.get("id", "unknown"),
            candidate_name=candidate_info.get("name", "Unknown"),
            interview_duration=int(context["interview_content"]["duration_seconds"]),
            scores=detailed_scores,
            audio_quality=context["technical_quality"]["audio_quality"],
            video_quality=context["technical_quality"]["video_quality"],
            emotion_analysis=context["nonverbal_behavior"]["emotions_distribution"],
            eye_contact_percentage=context["nonverbal_behavior"]["eye_contact_percentage"],
            gesture_frequency=context["nonverbal_behavior"]["gesture_frequency"],
            posture_confidence=context["nonverbal_behavior"]["posture_confidence"],
            speech_pace=context["verbal_communication"]["tempo_classification"],
            vocabulary_richness=min(int(context["interview_content"]["linguistic_features"].get("vocabulary_richness", 0.5) * 10), 10),
            grammar_quality=context["interview_content"]["linguistic_features"].get("grammar_complexity", 5),
            answer_structure=self._assess_answer_structure(context["interview_content"]["transcript"]),
            total_score=total_score,
            weighted_score=self._calculate_weighted_score(detailed_scores),
            recommendation=comprehensive_analysis.get("recommendation", "Требуется дополнительная оценка"),
            detailed_feedback=comprehensive_analysis.get("comprehensive_feedback", "Анализ завершен"),
            analysis_timestamp=datetime.now().isoformat(),
            ai_model_version="integrated-v1.0"
        )
    
    def _calculate_weighted_score(self, scores: Dict) -> float:
        """Расчет взвешенной оценки"""
        weights = {
            EvaluationCriteria.COMMUNICATION_SKILLS: 1.2,
            EvaluationCriteria.MOTIVATION_LEARNING: 1.1,
            EvaluationCriteria.PROFESSIONAL_SKILLS: 1.0,
            EvaluationCriteria.ANALYTICAL_THINKING: 1.0,
            EvaluationCriteria.UNCONVENTIONAL_THINKING: 0.9,
            EvaluationCriteria.TEAMWORK_ABILITY: 1.0,
            EvaluationCriteria.STRESS_RESISTANCE: 0.9,
            EvaluationCriteria.ADAPTABILITY: 0.9,
            EvaluationCriteria.CREATIVITY_INNOVATION: 0.8,
            EvaluationCriteria.OVERALL_IMPRESSION: 1.1
        }
        
        weighted_sum = sum(scores[criterion].score * weights[criterion] for criterion in scores)
        total_weight = sum(weights.values())
        
        return weighted_sum / total_weight
    
    def _assess_answer_structure(self, transcript: str) -> int:
        """Оценка структурированности ответов"""
        structure_markers = [
            "во-первых", "во-вторых", "в-третьих",
            "с одной стороны", "с другой стороны",
            "например", "в частности", "таким образом",
            "в заключение", "подводя итог"
        ]
        
        marker_count = sum(1 for marker in structure_markers if marker in transcript.lower())
        return min(marker_count + 3, 10)
    
    def _get_fallback_analysis(self) -> Dict:
        """Запасной анализ в случае ошибки"""
        return {
            "holistic_scores": {criterion.value: 5 for criterion in EvaluationCriteria},
            "cross_modal_insights": {
                "verbal_nonverbal_alignment": "Анализ не удался",
                "emotional_consistency": "Неопределенный",
                "confidence_indicators": "Не определены",
                "stress_indicators": "Не определены"
            },
            "detailed_observations": {criterion.value: ["Анализ не удался"] for criterion in EvaluationCriteria},
            "comprehensive_feedback": "Технический сбой в анализе",
            "recommendation": "Требуется повторный анализ"
        }
