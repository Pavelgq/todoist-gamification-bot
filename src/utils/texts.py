"""
Модуль с текстовыми сообщениями для бота.
Позволяет централизованно управлять текстами и упрощает добавление локализации.
"""


class Messages:
    """Класс с пользовательскими сообщениями, сгруппированными по категориям."""

    # ==================== Авторизация ====================
    AUTH_REQUIRED = "Сначала авторизуйтесь через /start"
    AUTH_SUCCESS = "Авторизация прошла успешно!"

    # ==================== Команда /start ====================
    START_ALREADY_AUTHORIZED = (
        "Вы уже авторизованы в Todoist!\n"
        "Введите /help или выберите команду из меню, чтобы увидеть всё, что я умею."
    )
    START_AUTH_REQUEST = "Пожалуйста, авторизуйте доступ к вашему Todoist аккаунту:"
    START_AUTH_BUTTON = "Авторизовать Todoist"
    START_AFTER_AUTH = "После авторизации введите /help или выберите команду из меню."
    START_ERROR = "Произошла ошибка при обработке команды"

    # ==================== Команда /help ====================
    HELP_TEXT = (
        "📋 Список доступных команд:\n\n"
        "• /start — начать работу с ботом и авторизовать Todoist.\n"
        "• /help — показать это сообщение со списком команд.\n"
        "• /tags — показать список ваших тегов в Todoist.\n"
        "• /statistic [период] — показать статистику по наградам за период (доступно: неделя, месяц, '3 месяца').\n"
        "• /newreward — создать новую награду.\n"
        "• /setreward — привязать награду к тегу Todoist.\n"
        "• /rewards — показать ваши добавленные награды.\n"
    )
    HELP_ERROR = "❌ Ошибка при выводе списка команд."

    # ==================== Команда /tags ====================
    TAGS_NONE = "У вас нет тегов в Todoist"
    TAGS_LIST_HEADER = "Ваши теги:\n"
    TAGS_ERROR = "❌ Ошибка при получении списка тегов."

    # ==================== Команда /statistic ====================
    @staticmethod
    def stats_period_empty(period: str) -> str:
        """Сообщение об отсутствии статистики за период."""
        return f"Нет начисленных наград за период «{period}»."

    @staticmethod
    def stats_period_header(period: str) -> str:
        """Заголовок статистики за период."""
        return f"🌟 Статистика за период «{period}»:\n\n"

    @staticmethod
    def stats_item(reward_name: str, reward_unit: str, total_value: float) -> str:
        """Элемент статистики (одна награда)."""
        return f"• {reward_name} ({reward_unit}): {total_value:.2f}\n"

    STATS_ERROR = "Произошла ошибка при подсчёте статистики."

    # ==================== Награды: создание ====================
    REWARD_CREATE_START = "Создаем новую награду!\nВведите название (например: 'Очки опыта'):"
    
    @staticmethod
    def reward_name_confirmed(name: str) -> str:
        """Подтверждение названия награды."""
        return f"Название: {name}\nТеперь введите единицы измерения (например: 'раз'):"

    REWARD_NAME_NOT_FOUND = "❌ Не найдено название награды"
    
    @staticmethod
    def reward_created(reward_name: str, reward_unit: str) -> str:
        """Сообщение об успешном создании награды."""
        return f"🎉 Награда создана!\n{reward_name} ({reward_unit})"

    REWARD_CREATE_ERROR = "❌ Ошибка при создании"
    REWARD_CREATE_CANCELED = "Создание награды отменено."

    # ==================== Награды: привязка к тегу ====================
    REWARD_NO_REWARDS = "❌ У вас нет наград. Создайте через /newreward"
    REWARD_SELECT_FOR_LINK = "Выберите награду для привязки:"
    REWARD_ERROR_GETTING = "Ошибка получения наград."
    REWARD_SELECT_TAG = "Выберите тег для привязки:"
    REWARD_NO_TAGS = "❌ У вас нет тегов в Todoist"
    REWARD_SELECT_TAG_ERROR = "Произошла ошибка при выборе тега."
    REWARD_ENTER_VALUE = "Введите, сколько единиц награды давать за этот тег (например, 1.5):"
    REWARD_INVALID_VALUE = "❌ Пожалуйста, введите число (например: 1.5)"
    REWARD_ALREADY_LINKED = "⚠️ Эта награда уже привязана к тегу\n"
    REWARD_LINKED_SUCCESS = "✅ Награда привязана к тегу!"
    REWARD_SAVE_ERROR = "❌ Ошибка при сохранении"

    # ==================== Команда /rewards ====================
    REWARDS_NONE = "У вас пока нет наград. Создайте через /newreward"
    REWARDS_LIST_HEADER = "🎁 Добавленные награды:\n"
    
    @staticmethod
    def rewards_item(reward_name: str, reward_unit: str) -> str:
        """Элемент списка наград."""
        return f"\n• {reward_name} ({reward_unit})"

    REWARDS_LIST_ERROR = "Ошибка вывода наград."

    # ==================== Описания команд для меню ====================
    COMMAND_START_DESC = "Начать работу и авторизовать Todoist"
    COMMAND_HELP_DESC = "Показать список команд"
    COMMAND_TAGS_DESC = "Показать список тегов Todoist"
    COMMAND_STATISTIC_DESC = "Статистика по наградам (по умолчанию за неделю)"
    COMMAND_NEWREWARD_DESC = "Создать новую награду"
    COMMAND_SETREWARD_DESC = "Привязать награду к тегу Todoist"
    COMMAND_REWARDS_DESC = "Показать ваши награды"

    # ==================== Сервер (OAuth callback) ====================
    SERVER_MISSING_PARAMS = "Missing code or state parameters"
    SERVER_INVALID_STATE = "Некорректный state — попробуйте авторизоваться заново через бот."
    SERVER_AUTH_ERROR_HTML = "<h1>Ошибка</h1><p>Ошибка авторизации. </p>"
    
    @staticmethod
    def server_auth_error_detail(error: str) -> str:
        """HTML страница с деталями ошибки авторизации."""
        return f"<h1>Ошибка авторизации</h1><p>{error}</p>"

    SERVER_AUTH_SUCCESS_HTML = """
            <h1>Авторизация успешна!</h1>
            <p>Теперь вы можете закрыть эту вкладку и вернуться в бота</p>
            <script>window.close();</script>
        """
