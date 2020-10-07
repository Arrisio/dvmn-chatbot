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
    requested_timestamp = datetime.timestamp(datetime.now())
    requested_timestamp = datetime.timestamp(datetime.fromisoformat("2019-01-01"))
    while True:
        try:
            response = requests.get(
                DVMN_API_URL,
                headers={"Authorization": f"Token {DVMN_TOKEN}"},
                params={"timestamp": requested_timestamp},
            )
            response_payload = response.json()
            if response_payload.get("status") == "found":
                requested_timestamp = response_payload["last_attempt_timestamp"]
                notify_attempts_results(response_payload["new_attempts"])
        except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ) as e:
            logging.warning(e)
            time.sleep(CONNECTION_ERROR_SLEEP_TIME)
            continue
        except Exception as e:
            logging.error(e)
            raise e


if __name__ == "__main__":
    run()
