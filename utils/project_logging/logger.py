import os
import sys
from typing import Union

from loguru import logger

from .notifier import notify_telegram


def configure_logger(
    set_default_prod_configuration: Union[bool, None] = None,
    level: Union[None, str, int] = "DEBUG",
    context_extra: bool = False,
    extra_vars: list = [],
    notify_with_telegram: bool = False,
) -> None:
    """
    Процедура конфигурирует логер Loguru, в зависимости от среды эксплуатации логгера

        :param set_default_prod_configuration: Автоматически применяются настройки для боевого ражима: Вывод в json формат; ERROR и CRITICAL логи выводятся в stderr. Если True - Все остальные параметры (кроме level) игнорируются
        :param level: уровень логгировая
        :param context_extra:  бубет ли в выдо добавлятьсясловарь с extra параметраими
        :param extra_vars: список c параметрами, которые будут выводиться в табличном (т.е. не json) режиме
        :param notify_with_telegram: Надо ли отправлять уведомления об ошибках через телегу. Если да, то должны быть определены переменные окружения BOT_TOKEN и SUBSCRIBER_CHAT_ID
        :return:
    """

    if set_default_prod_configuration is None:
        set_default_prod_configuration = _autodefine_is_prod_configuration()

    logger.configure(
        **_get_loguru_config(
            level=level,
            extra_vars=extra_vars,
            set_default_prod_configuration=set_default_prod_configuration,
            context_extra=context_extra,
        )
    )

    if notify_with_telegram:
        logger.add(
            sink=notify_telegram,
            format="{level}-{name:<12}-{function}-line:{line} message:{message}",
            level="ERROR",
        )


def _get_loguru_config(
    set_default_prod_configuration: bool = False,
    level: Union[None, str, int] = "DEBUG",
    extra_vars: list = [],
    context_extra: bool = False,
) -> dict:
    if set_default_prod_configuration:

        return {
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

    extra_vars_substring = " | ".join(
        ["{extra[" + var + "]:>16}" for var in extra_vars]
    )
    if context_extra:
        extra_vars_substring += " |{extra}"

    return {
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


def _autodefine_is_prod_configuration():
    if os.getenv(
        "HOSTNAME"
    ):  # эту переменную как правило создает докер. завязывемся на нее, чтоб определить - находимся ли мы в режиме разработки или боя. Возможно, в будущем надо будет поискать дургой спопоб
        return True

    return False


def _stdout_filter(record):
    return record["level"].no <= logger.level("WARNING").no


logger.configure(**_get_loguru_config())  # если нас устраивают дефолтовые настройки и мы не хотим конфигуряцить логгер в коде
