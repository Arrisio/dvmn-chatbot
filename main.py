import os
import requests
from datetime import datetime
import time

from src.tlg import notify_attempts_results

import logging.config

logging.config.fileConfig("configs/logging.conf")


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
            response_payload = response.json()
            if response_payload.get("status") == "found":
                attempt_results = response_payload["new_attempts"]
                logging.debug(
                    "devman api return attampts info",
                    extra={"attemptsNumber": len(attempt_results)},
                )
                requested_timestamp = response_payload["last_attempt_timestamp"]

                notify_attempts_results(attempt_results)
            elif response_payload.get("status") == "timeout":
                logging.debug("devman api request rimeout")
            else:
                raise Exception("unkown response format from devman api")
        except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ) as e:
            logging.warning(e.msg)
            time.sleep(CONNECTION_ERROR_SLEEP_TIME)
        except Exception as e:
            logging.exception("Fatal error in main loop", exc_info=True)
            raise e


if __name__ == "__main__":
    run()
