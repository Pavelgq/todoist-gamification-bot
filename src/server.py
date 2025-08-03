from flask import Flask, request
import requests
import logging
from src.config import Config
from src.database import SessionLocal
from src.models import User

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/auth/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    if not code or not state:
        return "Missing code or state parameters", 400

    try:
        user_id = int(state)
    except Exception:
        return "Некорректный state — попробуйте авторизоваться заново через бот.", 400

    try:
        response = requests.post(
            "https://todoist.com/oauth/access_token",
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
            logger.error(f"Нет access_token в ответе: {token_data}")
            return "<h1>Ошибка</h1><p>Ошибка авторизации. </p>", 400

        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id)
                db.add(user)
            user.todoist_token = access_token
            db.commit()
        
        return """
            <h1>Авторизация успешна!</h1>
            <p>Теперь вы можете закрыть эту вкладку и вернуться в бота</p>
            <script>window.close();</script>
        """

    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}", exc_info=True)
        return f"<h1>Ошибка авторизации</h1><p>{str(e)}</p>", 400

def run_server():
    app.run(port=5000, debug=False, host="0.0.0.0")
