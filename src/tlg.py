import os
from typing import NoReturn, Union

import telegram

from utils.project_logging import logger


def notify_attempts_results(
    attempts_results: list,
    bot: telegram.Bot = telegram.Bot(token=os.environ.get("TG_BOT_TOKEN")),
    chat_id: Union[str, int] = os.environ.get("TG_SUBSCRIBER_CHAT_ID"),
) -> NoReturn:

    for attempt_result in attempts_results:
        bot.send_message(
            chat_id=chat_id,
            parse_mode=telegram.parsemode.ParseMode.MARKDOWN,
            text=generate_message(attempt_result),
        )
        logger.debug("attempt result notified", extra=attempt_result)


def generate_message(attempt_result: dict) -> str:
    if attempt_result["is_negative"]:
        check_result = "*возвращена на доработку*"
    else:
        check_result = "*принята*"
    return (
        f"Задача [{attempt_result['lesson_title']}]"
        f"(https://dvmn.org{attempt_result['lesson_url']}) {check_result}"
    )
