from todoist_api_python.api import TodoistAPI
from src.config import Config
from urllib.parse import urlencode
from typing import Optional, List, Any

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
    def get_labels(access_token: str) -> Optional[List[Any]]:
        """Получает метки (labels) пользователя."""
        try:
            api = TodoistAPI(access_token)
            return api.get_labels()
        except Exception as e:
            print(f"Error fetching labels: {e}")
            return None

    @staticmethod
    def get_completed_tasks(access_token: str, since: Optional[str] = None, limit: int = 100) -> Optional[List[Any]]:
        """
        Получает завершённые задачи с опцией since.
        """
        try:
            api = TodoistAPI(access_token)
            return api.get_completed_items(since=since, limit=limit)
        except Exception as e:
            print(f"Error fetching completed tasks: {e}")
            return None
