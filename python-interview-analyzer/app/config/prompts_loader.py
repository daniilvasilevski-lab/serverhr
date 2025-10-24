"""
Загрузчик промптов из YAML файла для легкого редактирования

ВАЖНО: Для изменения промптов редактируйте файл prompts.yaml в корне проекта!
После изменения промптов перезапустите приложение: docker-compose restart app
"""

import yaml
import os
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class PromptsLoader:
    """Класс для загрузки и управления промптами из YAML файла"""

    _instance = None
    _prompts_data: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._prompts_data is None:
            self.reload()

    @property
    def prompts_file(self) -> str:
        """Путь к файлу с промптами"""
        # Поднимаемся на 3 уровня вверх от app/config/prompts_loader.py
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, 'prompts.yaml')

    def reload(self):
        """Перезагрузка промптов из файла"""
        try:
            if os.path.exists(self.prompts_file):
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    self._prompts_data = yaml.safe_load(f)
                logger.info(f"✅ Prompts loaded from: {self.prompts_file}")
            else:
                logger.warning(f"⚠️ Prompts file not found: {self.prompts_file}")
                self._prompts_data = self._get_fallback_prompts()
        except Exception as e:
            logger.error(f"❌ Error loading prompts: {e}")
            self._prompts_data = self._get_fallback_prompts()

    def _get_fallback_prompts(self) -> Dict:
        """Минимальные fallback промпты на случай проблем"""
        return {
            "system_prompts": {
                "integrated_analyzer": {
                    "ru": "Ты эксперт-психолог и HR-специалист с 15+ лет опыта. Анализируй целостно.",
                    "en": "You are an expert psychologist and HR specialist with 15+ years experience. Analyze holistically.",
                },
                "cv_analyzer": {
                    "ru": "Ты профессиональный HR-аналитик. Анализируй объективно.",
                    "en": "You are a professional HR analyst. Analyze objectively.",
                }
            }
        }

    def get_system_prompt(self, analyzer_type: str, language: str = "ru") -> str:
        """
        Получение системного промпта для анализатора

        Args:
            analyzer_type: Тип анализатора (integrated_analyzer, cv_analyzer, etc.)
            language: Язык промпта (ru, en, pl)

        Returns:
            str: Системный промпт
        """
        if not self._prompts_data:
            self.reload()

        system_prompts = self._prompts_data.get('system_prompts', {})
        analyzer_prompts = system_prompts.get(analyzer_type, {})

        # Пробуем получить промпт для указанного языка
        prompt = analyzer_prompts.get(language)

        # Fallback на русский если нет нужного языка
        if not prompt:
            prompt = analyzer_prompts.get('ru', '')

        if not prompt:
            logger.warning(f"⚠️ No prompt found for {analyzer_type}/{language}")

        return prompt

    def get_criteria_prompt(self, criterion: str, language: str = "ru") -> str:
        """
        Получение промпта для оценки конкретного критерия

        Args:
            criterion: Название критерия
            language: Язык

        Returns:
            str: Промпт для критерия
        """
        if not self._prompts_data:
            self.reload()

        criteria_prompts = self._prompts_data.get('evaluation_criteria_prompts', {})
        criterion_prompts = criteria_prompts.get(criterion, {})

        return criterion_prompts.get(language, criterion_prompts.get('ru', ''))

    def get_recommendation_prompt(self, score: int, language: str = "ru") -> str:
        """
        Получение рекомендации на основе общего балла

        Args:
            score: Общий балл (0-100)
            language: Язык

        Returns:
            str: Текст рекомендации
        """
        if not self._prompts_data:
            self.reload()

        rec_prompts = self._prompts_data.get('recommendation_prompts', {})

        # Определяем категорию по баллу
        for category, data in rec_prompts.items():
            threshold = data.get('threshold', 0)
            if score >= threshold:
                return data.get(language, data.get('ru', 'Требуется оценка'))

        return "Требуется дополнительная оценка"

    def get_special_instruction(self, key: str) -> Any:
        """
        Получение специальной инструкции

        Args:
            key: Ключ инструкции

        Returns:
            Any: Значение инструкции
        """
        if not self._prompts_data:
            self.reload()

        special = self._prompts_data.get('special_instructions', {})
        return special.get(key)

    def get_criteria_weights(self) -> Dict[str, float]:
        """Получение весов критериев для расчета взвешенной оценки"""
        if not self._prompts_data:
            self.reload()

        special = self._prompts_data.get('special_instructions', {})
        return special.get('criteria_weights', {})

    def is_strict_mode(self) -> bool:
        """Проверка, включен ли строгий режим оценки"""
        return self.get_special_instruction('strict_mode') or False

    def requires_examples(self) -> bool:
        """Проверка, требуются ли примеры для каждой оценки"""
        return self.get_special_instruction('require_examples') or False

    def get_min_score_for_hire(self) -> int:
        """Минимальный балл для рекомендации к найму"""
        return self.get_special_instruction('min_score_for_hire') or 70


# Глобальный экземпляр загрузчика
_prompts_loader = None


def get_prompts_loader() -> PromptsLoader:
    """Получение глобального экземпляра загрузчика промптов"""
    global _prompts_loader
    if _prompts_loader is None:
        _prompts_loader = PromptsLoader()
    return _prompts_loader


# Удобные функции для быстрого доступа
def get_system_prompt(analyzer_type: str, language: str = "ru") -> str:
    """Быстрый доступ к системному промпту"""
    return get_prompts_loader().get_system_prompt(analyzer_type, language)


def get_recommendation(score: int, language: str = "ru") -> str:
    """Быстрый доступ к рекомендации"""
    return get_prompts_loader().get_recommendation_prompt(score, language)


def reload_prompts():
    """Перезагрузка всех промптов (для hot-reload)"""
    get_prompts_loader().reload()
    logger.info("🔄 Prompts reloaded successfully")
