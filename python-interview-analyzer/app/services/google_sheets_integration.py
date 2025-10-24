"""
Обновленный сервис для работы с Google Sheets с правильным маппингом колонок
"""

import logging
from typing import Dict, List, Any, Optional
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime

from ..models.evaluation_criteria import InterviewAnalysis, EvaluationCriteria
from ..config.settings import settings

logger = logging.getLogger(__name__)


class GoogleSheetsIntegration:
    """Интеграция с Google Sheets для автоматической обработки интервью"""

    def __init__(self):
        self.gc = None
        self.source_sheet = None
        self.results_sheet = None

        # Входные колонки (нумерация с 0)
        self.INPUT_COLUMNS = {
            'ID': 0,            # A
            'Name': 1,          # B
            'Email': 2,         # C
            'Phone': 3,         # D
            'Preferences': 4,   # E
            'CV_gcs': 5,        # F
            'video_gcs': 6,     # G
            'CV_URL': 7,        # H
            'Video_URL': 8,     # I
            'created_at': 9,    # J
            'Questions_URL': 10,# K
            'Processed': 11     # L
        }

        # Выходные колонки (соответствие критериям)
        self.OUTPUT_COLUMNS_MAP = {
            'ID': 0,                    # A
            'Name': 1,                  # B
            'Email': 2,                 # C
            'Phone': 3,                 # D
            'Language': 4,              # E
            'Communication': 5,         # F - коммуникативные навыки
            'Motivation': 6,            # G - мотивация к обучению
            'Technical': 7,             # H - профессиональные навыки
            'Analytical': 8,            # I - аналитическое мышление
            'Creative': 9,              # J - креативность (unconventional_thinking + creativity_innovation)
            'Teamwork': 10,             # K - командная работа
            'Stress_Resistance': 11,    # L - стрессоустойчивость
            'Adaptability': 12,         # M - адаптивность
            'Overall_Score': 13,        # N - общий балл
            'Recommendation': 14        # O - рекомендация
        }

        self.setup_google_sheets()

    def setup_google_sheets(self):
        """Настройка подключения к Google Sheets"""
        try:
            if not settings.google_service_account_key:
                logger.warning("Google service account key not configured")
                return

            # Проверяем существование файла
            if not os.path.exists(settings.google_service_account_key):
                logger.error(f"Service account key file not found: {settings.google_service_account_key}")
                return

            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]

            creds = Credentials.from_service_account_file(
                settings.google_service_account_key,
                scopes=scope
            )
            self.gc = gspread.authorize(creds)
            logger.info("✅ Google Sheets connection established")

            # Подключение к таблицам
            if settings.source_sheet_url:
                self.source_sheet = self.gc.open_by_url(settings.source_sheet_url).sheet1
                logger.info(f"✅ Connected to source sheet: {self.source_sheet.title}")

            if settings.results_sheet_url:
                self.results_sheet = self.gc.open_by_url(settings.results_sheet_url).sheet1
                logger.info(f"✅ Connected to results sheet: {self.results_sheet.title}")
                self._ensure_results_headers()

        except Exception as e:
            logger.error(f"❌ Failed to setup Google Sheets: {e}")
            raise

    def _ensure_results_headers(self):
        """Проверка и создание заголовков в таблице результатов"""
        try:
            if not self.results_sheet:
                return

            expected_headers = [
                'ID', 'Name', 'Email', 'Phone', 'Language',
                'Communication', 'Motivation', 'Technical', 'Analytical',
                'Creative', 'Teamwork', 'Stress_Resistance', 'Adaptability',
                'Overall_Score', 'Recommendation'
            ]

            # Получаем текущие заголовки
            current_headers = self.results_sheet.row_values(1)

            # Если заголовков нет или они отличаются, устанавливаем правильные
            if not current_headers or current_headers != expected_headers:
                self.results_sheet.update('A1:O1', [expected_headers])

                # Форматируем заголовки
                self.results_sheet.format('A1:O1', {
                    'textFormat': {'bold': True, 'fontSize': 11},
                    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                    'horizontalAlignment': 'CENTER'
                })

                logger.info("✅ Results sheet headers configured")

        except Exception as e:
            logger.error(f"Failed to ensure results headers: {e}")

    async def scan_for_unprocessed_interviews(self) -> List[Dict[str, Any]]:
        """Сканирует входную таблицу на наличие необработанных интервью"""
        if not self.source_sheet:
            logger.error("Source sheet not configured")
            return []

        try:
            all_values = self.source_sheet.get_all_values()

            if not all_values or len(all_values) < 2:
                logger.info("No data found in source sheet")
                return []

            headers = all_values[0]
            rows = all_values[1:]

            unprocessed = []

            for row_idx, row in enumerate(rows, start=2):
                # Проверяем длину строки
                if len(row) <= self.INPUT_COLUMNS['Processed']:
                    continue

                # Проверяем поле Processed
                processed_value = row[self.INPUT_COLUMNS['Processed']].strip() if len(row) > self.INPUT_COLUMNS['Processed'] else ''

                if not processed_value or processed_value != '1':
                    # Проверяем наличие Video_URL
                    video_url = row[self.INPUT_COLUMNS['Video_URL']].strip() if len(row) > self.INPUT_COLUMNS['Video_URL'] else ''

                    if video_url:
                        interview_data = {
                            'row_number': row_idx,
                            'id': row[self.INPUT_COLUMNS['ID']],
                            'name': row[self.INPUT_COLUMNS['Name']],
                            'email': row[self.INPUT_COLUMNS['Email']] if len(row) > self.INPUT_COLUMNS['Email'] else '',
                            'phone': row[self.INPUT_COLUMNS['Phone']] if len(row) > self.INPUT_COLUMNS['Phone'] else '',
                            'preferences': row[self.INPUT_COLUMNS['Preferences']] if len(row) > self.INPUT_COLUMNS['Preferences'] else '',
                            'cv_url': row[self.INPUT_COLUMNS['CV_URL']] if len(row) > self.INPUT_COLUMNS['CV_URL'] else '',
                            'video_url': video_url,
                            'questions_url': row[self.INPUT_COLUMNS['Questions_URL']] if len(row) > self.INPUT_COLUMNS['Questions_URL'] else '',
                            'created_at': row[self.INPUT_COLUMNS['created_at']] if len(row) > self.INPUT_COLUMNS['created_at'] else ''
                        }

                        unprocessed.append(interview_data)
                        logger.info(f"📋 Found unprocessed interview: {interview_data['name']} (Row {row_idx})")

            logger.info(f"✅ Found {len(unprocessed)} unprocessed interviews")
            return unprocessed

        except Exception as e:
            logger.error(f"❌ Error scanning for unprocessed interviews: {e}")
            return []

    async def save_analysis_results(self, analysis: InterviewAnalysis, candidate_info: Dict[str, Any]) -> bool:
        """
        Сохраняет результаты анализа в выходную таблицу

        Args:
            analysis: Результат анализа интервью
            candidate_info: Информация о кандидате (включая email, phone)

        Returns:
            bool: True если успешно сохранено
        """
        if not self.results_sheet:
            logger.error("Results sheet not configured")
            return False

        try:
            # Определяем язык
            language = self._detect_language(analysis.detailed_feedback)

            # Извлекаем оценки по критериям
            scores = analysis.scores

            # Формируем строку результатов
            results_row = [
                candidate_info.get('id', ''),                                              # A: ID
                analysis.candidate_name,                                                   # B: Name
                candidate_info.get('email', ''),                                           # C: Email
                candidate_info.get('phone', ''),                                           # D: Phone
                language.upper(),                                                          # E: Language
                scores.get(EvaluationCriteria.COMMUNICATION_SKILLS, {}).get('score', 0),  # F: Communication
                scores.get(EvaluationCriteria.MOTIVATION_LEARNING, {}).get('score', 0),   # G: Motivation
                scores.get(EvaluationCriteria.PROFESSIONAL_SKILLS, {}).get('score', 0),   # H: Technical
                scores.get(EvaluationCriteria.ANALYTICAL_THINKING, {}).get('score', 0),   # I: Analytical
                self._calculate_creative_score(scores),                                     # J: Creative
                scores.get(EvaluationCriteria.TEAMWORK_ABILITY, {}).get('score', 0),      # K: Teamwork
                scores.get(EvaluationCriteria.STRESS_RESISTANCE, {}).get('score', 0),     # L: Stress_Resistance
                scores.get(EvaluationCriteria.ADAPTABILITY, {}).get('score', 0),          # M: Adaptability
                analysis.total_score,                                                       # N: Overall_Score
                analysis.recommendation                                                     # O: Recommendation
            ]

            # Добавляем строку в таблицу
            self.results_sheet.append_row(results_row)

            logger.info(f"✅ Results saved for candidate: {analysis.candidate_name} (ID: {candidate_info.get('id')})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save analysis results: {e}")
            return False

    async def mark_as_processed(self, interview_data: Dict[str, Any]) -> bool:
        """
        Отмечает интервью как обработанное во входной таблице

        Args:
            interview_data: Данные интервью с row_number

        Returns:
            bool: True если успешно
        """
        if not self.source_sheet:
            logger.error("Source sheet not configured")
            return False

        try:
            row_number = interview_data['row_number']
            processed_column = chr(ord('A') + self.INPUT_COLUMNS['Processed'])
            cell_address = f"{processed_column}{row_number}"

            # Устанавливаем значение "1"
            self.source_sheet.update(cell_address, "1")

            logger.info(f"✅ Marked as processed: {interview_data['name']} (Row {row_number})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to mark as processed: {e}")
            return False

    def _calculate_creative_score(self, scores: Dict) -> int:
        """
        Вычисляет оценку креативности как среднее между
        нестандартным мышлением и креативностью/инновациями
        """
        unconventional = scores.get(EvaluationCriteria.UNCONVENTIONAL_THINKING, {}).get('score', 0)
        creativity = scores.get(EvaluationCriteria.CREATIVITY_INNOVATION, {}).get('score', 0)

        if unconventional or creativity:
            return int((unconventional + creativity) / 2)
        return 0

    def _detect_language(self, text: str) -> str:
        """
        Определяет язык текста

        Args:
            text: Текст для анализа

        Returns:
            str: Код языка ('ru', 'en', 'pl')
        """
        if not text:
            return 'en'

        text_lower = text.lower()

        # Проверяем наличие кириллицы
        has_cyrillic = any(ord('а') <= ord(char) <= ord('я') or char == 'ё' for char in text_lower)
        if has_cyrillic:
            return 'ru'

        # Проверяем польские специальные символы
        polish_chars = ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż']
        has_polish = any(char in text_lower for char in polish_chars)
        if has_polish:
            return 'pl'

        # По умолчанию английский
        return 'en'

    async def process_all_unprocessed(self, analyzer, cv_analyzer, questions_analyzer) -> Dict[str, int]:
        """
        Обрабатывает все необработанные интервью

        Args:
            analyzer: Экземпляр IntegratedInterviewAnalyzer
            cv_analyzer: Экземпляр CVAnalyzer
            questions_analyzer: Экземпляр QuestionsAnalyzer

        Returns:
            Dict: Статистика обработки
        """
        stats = {
            'found': 0,
            'processed': 0,
            'failed': 0,
            'saved': 0
        }

        try:
            # Сканируем необработанные интервью
            unprocessed_interviews = await self.scan_for_unprocessed_interviews()
            stats['found'] = len(unprocessed_interviews)

            if not unprocessed_interviews:
                logger.info("ℹ️ No unprocessed interviews found")
                return stats

            logger.info(f"📊 Starting batch processing of {stats['found']} interviews...")

            # Обрабатываем каждое интервью
            for idx, interview_data in enumerate(unprocessed_interviews, 1):
                try:
                    logger.info("=" * 80)
                    logger.info(f"🎯 НАЧАЛО ОБРАБОТКИ КАНДИДАТА #{idx}/{stats['found']}")
                    logger.info(f"👤 Имя: {interview_data['name']}")
                    logger.info(f"🆔 ID: {interview_data['id']}")
                    logger.info(f"📧 Email: {interview_data['email']}")
                    logger.info(f"🎥 Видео: {interview_data['video_url'][:60]}...")
                    logger.info("=" * 80)

                    # Подготавливаем информацию о кандидате
                    candidate_info = {
                        'id': interview_data['id'],
                        'name': interview_data['name'],
                        'email': interview_data['email'],
                        'phone': interview_data['phone'],
                        'preferences': interview_data['preferences']
                    }

                    logger.info(f"⏳ Запуск анализа интервью для {interview_data['name']}...")

                    # Анализируем интервью
                    analysis_result = await analyzer.analyze_interview(
                        interview_data['video_url'],
                        candidate_info
                    )

                    if analysis_result:
                        stats['processed'] += 1

                        logger.info(f"✅ Анализ завершен успешно!")
                        logger.info(f"📊 Итоговая оценка: {analysis_result.total_score}/100")
                        logger.info(f"💡 Рекомендация: {analysis_result.recommendation}")

                        # Сохраняем результаты
                        logger.info(f"💾 Сохранение результатов в Google Sheets...")
                        if await self.save_analysis_results(analysis_result, candidate_info):
                            stats['saved'] += 1

                            # Отмечаем как обработанное
                            logger.info(f"✏️ Отметка интервью как обработанного...")
                            await self.mark_as_processed(interview_data)

                            logger.info(f"🎉 УСПЕШНО ОБРАБОТАН: {interview_data['name']} ({idx}/{stats['found']})")
                        else:
                            logger.error(f"❌ Ошибка при сохранении результатов для: {interview_data['name']}")
                    else:
                        stats['failed'] += 1
                        logger.error(f"❌ ОШИБКА АНАЛИЗА для: {interview_data['name']}")

                except Exception as e:
                    stats['failed'] += 1
                    logger.error(f"❌ Error processing {interview_data['name']}: {e}")

                # Небольшая пауза между обработками
                import asyncio
                await asyncio.sleep(2)

            logger.info(f"""
╔══════════════════════════════════════╗
║     BATCH PROCESSING COMPLETED       ║
╠══════════════════════════════════════╣
║ Found:      {stats['found']:3d}                     ║
║ Processed:  {stats['processed']:3d}                     ║
║ Saved:      {stats['saved']:3d}                     ║
║ Failed:     {stats['failed']:3d}                     ║
╚══════════════════════════════════════╝
            """)

            return stats

        except Exception as e:
            logger.error(f"❌ Error in batch processing: {e}")
            return stats


# Глобальный экземпляр сервиса
_sheets_integration = None


def get_sheets_integration() -> GoogleSheetsIntegration:
    """Получение глобального экземпляра сервиса Google Sheets"""
    global _sheets_integration
    if _sheets_integration is None:
        _sheets_integration = GoogleSheetsIntegration()
    return _sheets_integration
