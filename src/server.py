from flask import Flask, request
import requests

from .config import Config, TodoistConfig
from .services.todoist import TodoistService
from .utils.logger import get_logger
from .utils.texts import Messages

app = Flask(__name__)
logger = get_logger(__name__)

@app.route('/auth/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    if not code or not state:
        return Messages.SERVER_MISSING_PARAMS, 400

    try:
        user_id = int(state)
    except Exception:
        return Messages.SERVER_INVALID_STATE, 400

    try:
        response = requests.post(
            TodoistConfig.OAUTH_ACCESS_TOKEN_URL,
            data={
                "client_id": Config.TODOIST_CLIENT_ID,
                "client_secret": Config.TODOIST_CLIENT_SECRET,
                "code": code,
                "redirect_uri": Config.REDIRECT_URI
            },
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            logger.error("Нет access_token в ответе от Todoist", response_data=token_data, user_id=user_id)
            return Messages.SERVER_AUTH_ERROR_HTML, 400

        # Сохраняем токен через сервисный слой
        TodoistService.upsert_user_token(user_id, access_token)
        logger.info("Пользователь успешно авторизован в Todoist", user_id=user_id)
        
        return Messages.SERVER_AUTH_SUCCESS_HTML

    except Exception as e:
        logger.exception("Ошибка авторизации", error=str(e), user_id=user_id, code=code if 'code' in locals() else None)
        return Messages.server_auth_error_detail(str(e)), 400

def run_server():
    app.run(port=5001, debug=False, host="0.0.0.0")
