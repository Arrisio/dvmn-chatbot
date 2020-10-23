import os
import time
from datetime import datetime

import requests

from src.tlg import notify_attempts_results
from utils.project_logging import logger, configure_logger

DVMN_TOKEN = os.environ.get("DVMN_TOKEN")
DVMN_API_URL = "https://dvmn.org/api/long_polling/"
CONNECTION_ERROR_SLEEP_TIME = 60


class DvmnUnknownReponseStatusException(Exception):
    pass


@logger.catch(reraise=True)
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
            response.raise_for_status()
            response_payload = response.json()

            if response_payload.get("status") == "found":
                requested_timestamp = response_payload["last_attempt_timestamp"]
                attempt_results = response_payload["new_attempts"]
                logger.debug(
                    "devman api returns attempts info",
                    extra={"attemptsNumber": len(attempt_results)},
                )
                notify_attempts_results(attempt_results)

            elif response_payload.get("status") == "timeout":
                requested_timestamp = response_payload["timestamp_to_request"]
                logger.debug("devman api request timeout")

            else:
                raise DvmnUnknownReponseStatusException(str(response_payload))

        except requests.exceptions.ReadTimeout:
            logger.debug("devman api request timeout")

        except requests.exceptions.ConnectionError as e:
            logger.warning(e.msg)
            time.sleep(CONNECTION_ERROR_SLEEP_TIME)


if __name__ == "__main__":
    configure_logger(
        context_extra=True,
        json_forman=False,
        notify_with_telegram=True,
    )
    run()
