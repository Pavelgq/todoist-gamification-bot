"""Настройка структурированного логирования для приложения."""
import logging
import sys

import structlog


def setup_logging(level: str = "INFO") -> None:
    """Настраивает структурированное логирование для всего приложения.

    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Настраиваем стандартный logging для совместимости
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Настраиваем structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # В DEBUG режиме используем JSON, иначе красивый консольный вывод
    if level.upper() == "DEBUG":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Получить структурированный логгер для модуля.

    Args:
        name: Имя модуля (обычно __name__)

    Returns:
        Настроенный структурированный логгер
    """
    return structlog.get_logger(name)
