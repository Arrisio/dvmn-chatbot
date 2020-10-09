import os
import logging
from typing import NoReturn
import telegram


def notify_attempts_results(
    attempts_results: list, bot=telegram.Bot(token=os.environ.get("TLG_BOT_TOKEN"))
) -> NoReturn:
    chat_id = os.environ.get("SUBSCRIBER_CHAT_ID")
    for attempt_result in attempts_results:
        bot.send_message(
            chat_id=chat_id,
            parse_mode=telegram.parsemode.ParseMode.MARKDOWN,
            text=generate_message(attempt_result),
        )
        logging.debug("attempt result notified", extra=attempt_result)


def generate_message(attempt_result: dict) -> str:
    if attempt_result["is_negative"]:
        check_result = "*возвращена на доработку*"
    else:
        check_result = "*принята*"
    return (
        f"""Задача [{attempt_result['lesson_title']}]"""
        f"""(https://dvmn.org{attempt_result["lesson_url"]}) {check_result}"""
    )
