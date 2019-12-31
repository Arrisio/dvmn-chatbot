import os
import random
from typing import NoReturn, Dict
import telegram

BOT_TOKEN = os.environ.get("TLG_BOT_TOKEN")

def get_luminati_proxy() -> Dict[str, str]:
    username = os.environ.get("PROXY_USERNAME")
    port = os.environ.get("PROXY_PORT")
    password = os.environ.get("PROXY_PASSWORD")

    if not (username and port and password):
        return {}

    session_id = random.random()
    proxy_url = "http://%s-session-%s:%s@zproxy.lum-superproxy.io:%d" % (
        username,
        session_id,
        password,
        int(port),
    )
    return {"proxy_url": proxy_url}

def _init_tlg_bot_kwargs() -> dict:
    kwargs = {}
    proxy_url = get_luminati_proxy()
    if proxy_url:
        telegram_requester = telegram.utils.request.Request(**proxy_url)
        kwargs["request"] = telegram_requester

    return kwargs

def _init_bot():
    return telegram.Bot(token=BOT_TOKEN, **_init_tlg_bot_kwargs())


def notify_attempts_results(attempts_results: list, bot=_init_bot()) -> NoReturn:
    chat_id = _get_chat_id(bot)
    for attempt_result in attempts_results:
        bot.send_message(
            chat_id=chat_id,
            parse_mode=telegram.parsemode.ParseMode.MARKDOWN,
            text=generate_message(attempt_result),
        )


def generate_message(attempt_result: dict) -> str:

    if attempt_result["is_negative"]:
        check_result = "*возвращена на доработку*"
    else:
        check_result = "*принята*"
    return f""" Задача [{attempt_result['lesson_title']}](https://dvmn.org{attempt_result["lesson_url"]}) {check_result}"""








def _get_chat_id(bot):
    for update in bot.get_updates():
        d= update.to_dict()
        username = d['message']['chat']['username']
        if username == os.environ.get(
            "MY_USERNAME"
        ):
            return update.message.chat_id
