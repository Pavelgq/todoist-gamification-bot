"""Единый клиент для работы с Todoist API.

Инкапсулирует создание TodoistAPI, обработку ошибок, ретраи и логирование.
"""
import time
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlencode

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task, Label

from ..config import Config, TodoistConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TodoistClientError(Exception):
    """Базовое исключение для ошибок Todoist клиента."""
    pass


class TodoistClient:
    """Единый клиент для работы с Todoist API.
    
    Инкапсулирует создание TodoistAPI, обрабатывает ошибки, ретраи и логирует все вызовы.
    """
    
    def __init__(self, api_token: str):
        """Инициализирует клиент с токеном пользователя.
        
        Args:
            api_token: Токен доступа пользователя к Todoist API
        """
        if not api_token:
            raise TodoistClientError("API токен не может быть пустым")
        self.api_token = api_token
        self._api: Optional[TodoistAPI] = None
    
    @property
    def api(self) -> TodoistAPI:
        """Ленивая инициализация TodoistAPI."""
        if self._api is None:
            self._api = TodoistAPI(self.api_token)
        return self._api
    
    def _retry_on_error(self, func, *args, **kwargs):
        """Выполняет функцию с ретраями при ошибках.
        
        Args:
            func: Функция для выполнения
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы
            
        Returns:
            Результат выполнения функции
            
        Raises:
            TodoistClientError: Если все попытки неудачны
        """
        last_exception = None
        for attempt in range(TodoistConfig.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                last_exception = exc
                if attempt < TodoistConfig.MAX_RETRIES - 1:
                    delay = TodoistConfig.RETRY_DELAY_SECONDS * (attempt + 1)
                    logger.warning(
                        "Ошибка при вызове Todoist API, повторная попытка",
                        attempt=attempt + 1,
                        max_retries=TodoistConfig.MAX_RETRIES,
                        error_type=type(exc).__name__,
                        error=str(exc),
                        delay_seconds=delay
                    )
                    time.sleep(delay)
                else:
                    logger.exception(
                        "Все попытки вызова Todoist API исчерпаны",
                        max_retries=TodoistConfig.MAX_RETRIES,
                        error_type=type(exc).__name__,
                        error=str(exc)
                    )
        
        raise TodoistClientError(f"Не удалось выполнить запрос после {TodoistConfig.MAX_RETRIES} попыток") from last_exception
    
    def get_labels(self) -> List[Label]:
        """Получить список всех тегов (labels) пользователя.
        
        Returns:
            Список тегов пользователя. Пустой список при ошибке.
        """
        try:
            logger.debug("Запрос тегов из Todoist")
            labels = self._retry_on_error(self.api.get_labels)
            logger.info("Теги успешно получены из Todoist", labels_count=len(labels))
            return labels
        except TodoistClientError:
            raise
        except Exception as exc:
            logger.exception(
                "Ошибка при получении тегов из Todoist",
                error_type=type(exc).__name__,
                error=str(exc)
            )
            return []
    
    def get_completed_tasks(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Task]:
        """Получить список завершённых задач за период.
        
        Args:
            start_date: Начало периода
            end_date: Конец периода
            
        Returns:
            Список завершённых задач. Пустой список при ошибке.
        """
        try:
            logger.debug(
                "Запрос завершённых задач из Todoist",
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            def _fetch_tasks():
                paginator = self.api.get_completed_tasks_by_completion_date(
                    since=start_date,
                    until=end_date
                )
                return [task for task_batch in paginator for task in task_batch]
            
            tasks = self._retry_on_error(_fetch_tasks)
            logger.info(
                "Завершённые задачи успешно получены из Todoist",
                tasks_count=len(tasks),
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            return tasks
        except TodoistClientError:
            raise
        except Exception as exc:
            logger.exception(
                "Ошибка при получении завершённых задач из Todoist",
                error_type=type(exc).__name__,
                error=str(exc),
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            return []


class TodoistAuthHelper:
    """Вспомогательный класс для OAuth авторизации в Todoist."""
    
    @staticmethod
    def get_auth_url(state: str) -> str:
        """Сформировать URL для OAuth авторизации.
        
        Args:
            state: Параметр state для защиты от CSRF (обычно telegram_id пользователя)
            
        Returns:
            URL для редиректа на страницу авторизации Todoist
        """
        params = {
            "client_id": Config.TODOIST_CLIENT_ID,
            "scope": TodoistConfig.OAUTH_SCOPE,
            "state": state,
            "redirect_uri": Config.REDIRECT_URI
        }
        url = f"{TodoistConfig.OAUTH_AUTHORIZE_URL}?{urlencode(params)}"
        logger.debug("Сформирован URL для OAuth авторизации", state=state)
        return url
