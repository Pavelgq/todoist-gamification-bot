import logging
from datetime import datetime
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task, Label
from ..config import Config
from urllib.parse import urlencode
from typing import Optional, List

class TodoistHelper:
    @staticmethod
    def get_auth_url(state: str) -> str:
        params = {
            "client_id": Config.TODOIST_CLIENT_ID,
            "scope": "data:read_write,data:delete",
            "state": state,
            "redirect_uri": Config.REDIRECT_URI
        }
        return f"https://todoist.com/oauth/authorize?{urlencode(params)}"

    @staticmethod
    def get_labels(api_token: str, logger: Optional[logging.Logger] = None) -> List[Label]:
        logger = logger or logging.getLogger(__name__)
        api = TodoistAPI(api_token)
        try:
            return api.get_labels()
        except Exception as exc:
            logger.error("Error getting labels: %s: %s", type(exc).__name__, exc)
            return []

    @staticmethod
    def get_completed_tasks(api_token: str, start_date: datetime, end_date: datetime, logger: Optional[logging.Logger] = None) -> List[Task]:
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

