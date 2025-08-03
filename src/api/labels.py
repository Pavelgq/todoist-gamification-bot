import logging
from typing import List, Optional
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Label

def get_labels(api_token: str, logger: Optional[logging.Logger] = None) -> List[Label]:
    """
    Получает все теги из Todoist API.
    :param api_token: Токен для доступа к API Todoist.
    :param logger: Необязательный кастомный логгер.
    :return: Список объектов Label.
    """
    logger = logger or logging.getLogger(__name__)
    api = TodoistAPI(api_token)
    try:
        return [label for label_batch in api.get_labels() for label in label_batch]
    except Exception as exc:
        logger.error("Error getting labels: %s: %s", type(exc).__name__, exc)
        return []
