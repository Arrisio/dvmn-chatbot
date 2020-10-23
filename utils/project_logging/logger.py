import sys, os
from typing import Union
from loguru import logger
from .notifier import notify_telegram


def _stdout_filter(record):
    return record["level"].no <= logger.level("WARNING").no


def _get_loguru_config(
    extra_vars: list = [], json_forman: bool = False, context_extra: bool = False
) -> dict:
    if json_forman:

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
        return {
            "extra": {
                var: "" for var in extra_vars
            },  # ставим пустое значение по дефолту, чтоб не получать ошибку, если не передаем этот параметр
            "handlers": [
                {
                    "sink": sys.stdout,
                    "format": "<level>{level: <8}</level>|<cyan>{name:<12}</cyan>:<cyan>{function:<24}</cyan>:<cyan>{line}</cyan> - <level>{message:>32}</level> | "
                    + extra_vars_substring,
                },
            ],
        }


def auto_define_json_format():
    if os.getenv(
        "HOSTNAME"
    ):  # эту переменную как правило создает докер. завязывемся на нее, чтоб определить - находимся ли мы в режиме разработки или боя. Возможно, в будущем надо будет поискать дургой спопоб
        return True

    return False


def configure_logger(
    extra_vars: list = [],
    json_forman: Union[bool, None] = None,
    context_extra: bool = False,
    notify_with_telegram: bool = False,
) -> None:
    """
        Процедура конфигурирует логер Loguru, в зависимости от среды эксплуатации логгера
    1. В режиме разработки предполагается табличный (т.е. не json) режим вывода параметров: need_json_forman=False
    2. В табличном ражиме можно добалять  вывод extra-параметров: extra_vars=['custom_param1',]
    3. В боевом режиме предполагается вывод в json-формат.  need_json_forman=True
    4. В боевом ражеме логи ERROR и CRITICAL логи выводятся в stderr.  DEBUG,INFO и WARNING - в stdout

    :param extra_vars: список extra-параметров
    :param json_forman: будет ли  вывод в json формате
    :param context_extra: нужно ли в шаблон вывода добавлять {extra}. Использовать с конструкцией with logger.contextualize(task_id=123):
    :param notify_with_telegram: Надо ли отправлять уведомления об ошибках через телегу. Если да, то должны быть определены переменные окружения BOT_TOKEN и SUBSCRIBER_CHAT_ID

    :return:
    """

    logger.configure(
        **_get_loguru_config(
            extra_vars=extra_vars, json_forman=json_forman, context_extra=context_extra
        )
    )
    if notify_with_telegram:
        logger.add(
            sink=notify_telegram,
            format="{level}-{name:<12}-{function}-line:{line} message:{message}",
            level="ERROR",
        )


logger.configure(**_get_loguru_config())
