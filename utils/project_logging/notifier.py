import os
from typing import NoReturn, Union

import telegram


def notify_telegram(
    message: str,
    chat_id: Union[str, int] = os.environ.get("TG_SUBSCRIBER_CHAT_ID"),
    bot: telegram.Bot = telegram.Bot(token=os.environ.get("TG_BOT_TOKEN")),
) -> NoReturn:
    bot.send_message(
        chat_id=chat_id,
        parse_mode=telegram.parsemode.ParseMode.MARKDOWN,
        text=message,
    )
