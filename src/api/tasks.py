import logging
from typing import List, Optional
from datetime import datetime
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

def get_completed_tasks(api_token: str, start_date: datetime, end_date: datetime, logger: Optional[logging.Logger] = None) -> List[Task]:
    """
    Получает выполненные задачи за указанный период с помощью TodoistAPI.
    
    :param api_token: Токен доступа к Todoist.
    :param start_date: Начальная дата периода.
    :param end_date: Конечная дата периода.
    :param logger: Необязательный логгер.
    :return: Список объектов Task.
    """
    logger = logger or logging.getLogger(__name__)
    api = TodoistAPI(api_token)
    try:
        completed_tasks_paginator = api.get_completed_tasks_by_completion_date(
            since=start_date,
            until=end_date
        )
        return [task for task_batch in completed_tasks_paginator for task in task_batch]
    except Exception as exc:
        logger.error("Error getting completed tasks: %s: %s", type(exc).__name__, exc)
        return []
