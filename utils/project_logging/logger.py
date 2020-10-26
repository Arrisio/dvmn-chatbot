import os
import sys
from distutils.util import strtobool
from typing import Union

from loguru import logger

from .notifier import notify_telegram


def get_loguru_config(
    use_default_prod_configuration: bool = strtobool(
        os.getenv("LOGGING_DEFAULT_PROD_CONF", "FALSE")
    ),
    level: Union[None, str, int] = os.getenv("LOGGING_LEVEL", "INFO"),
    extra_vars: list = [],
    context_extra: bool = False,
    notify_with_telegram: bool = strtobool(
        os.getenv("LOGGING_NOTIFY_WITH_TELEGRAM", "FALSE")
    ),
) -> dict:
    """
    возвращает словарь с к конфигурацией логгера Loguru, в зависимости от среды эксплуатации и доп. параметров

    :param use_default_prod_configuration: Автоматически применяются настройки для боевого режима: Вывод в json формат; ERROR и CRITICAL логи выводятся в stderr. Если True - Все остальные параметры (кроме level) игнорируются
    :param level: уровень логгировая
    :param context_extra:  будет ли в выдов добавляться словарь с extra параметрами
    :param extra_vars: список c параметрами, которые будут выводиться в табличном (т.е. не json) режиме
    :param notify_with_telegram: Надо ли отправлять уведомления об ошибках через телегу. Если да, то должны быть определены переменные окружения BOT_TOKEN и SUBSCRIBER_CHAT_ID
    :return:
    """

    if use_default_prod_configuration:

        config = {
            "handlers": [
                {
                    "sink": sys.stderr,
                    "format": "",
                    "serialize": True,
                    "level": "ERROR",
                },
                {
                    "sink": sys.stdout,
                    "format": "",
                    "serialize": True,
                    "level": level,
                    "filter": _stdout_filter,
                },
            ]
        }
    else:
        extra_vars_substring = " | ".join(
            ["{extra[" + var + "]:>16}" for var in extra_vars]
        )
        if context_extra:
            extra_vars_substring += " |{extra}"

        config = {
            "extra": {
                var: "" for var in extra_vars
            },  # ставим пустое значение по дефолту, чтоб не получать ошибку, если не передаем этот параметр
            "handlers": [
                {
                    "sink": sys.stdout,
                    "level": level,
                    "format": "<level>{level: <8}</level>|<cyan>{name:<12}</cyan>:<cyan>{function:<24}</cyan>:<cyan>{line}</cyan> - <level>{message:>32}</level> | "
                    + extra_vars_substring,
                },
            ],
        }

    if notify_with_telegram:
        config["handlers"].append(
            {
                "sink": notify_telegram,
                "format": "{level}-{name:<12}-{function}-line:{line} message:{message}",
                "level": "ERROR",
            }
        )

        return config


def _stdout_filter(record):
    return record["level"].no <= logger.level("WARNING").no
