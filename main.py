import logging.config
import os
import time
from datetime import datetime

import requests

from src.tlg import notify_attempts_results

DVMN_TOKEN = os.environ.get("DVMN_TOKEN")
DVMN_API_URL = "https://dvmn.org/api/long_polling/"
CONNECTION_ERROR_SLEEP_TIME = 60


def run():
    requested_timestamp = datetime.timestamp(
        datetime.fromisoformat(os.getenv("CHECK_START_DATE")) or datetime.now()
    )
    while True:
        try:
            response = requests.get(
                DVMN_API_URL,
                headers={"Authorization": f"Token {DVMN_TOKEN}"},
                params={"timestamp": requested_timestamp},
            )
            response.raise_for_status()  # думаю, это исключение ловить на строке 55 except Exception as e:
            response_payload = response.json()

            if response_payload.get("status") == "found":
                requested_timestamp = response_payload["last_attempt_timestamp"]
                attempt_results = response_payload["new_attempts"]
                logging.debug(
                    "devman api returns attempts info",
                    extra={"attemptsNumber": len(attempt_results)},
                )
                notify_attempts_results(attempt_results)

            elif response_payload.get("status") == "timeout":
                requested_timestamp = response_payload["timestamp_to_request"]
                logging.debug("devman api request timeout")

            else:
                raise Exception("unkown response format from devman api")

        except requests.exceptions.ReadTimeout:
            logging.debug("devman api request timeout")

        except requests.exceptions.ConnectionError as e:
            logging.warning(e.msg)
            time.sleep(CONNECTION_ERROR_SLEEP_TIME)

        except Exception as e:
            logging.exception("Fatal error in main loop", exc_info=True)
            raise e
        # предполагаю, что отсылка к KISS была про этот блок
        # если это избыточно, то как залогировать exception в соответсвии с настройками логгера?


if __name__ == "__main__":
    logging.config.fileConfig("configs/logging.conf")
    run()
