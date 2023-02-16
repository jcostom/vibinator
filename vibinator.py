#!/usr/bin/env python3

import os
import logging
from time import sleep, strftime
import telegram
import RPi.GPIO

# --- To be passed in to container ---
# Mandatory Vars
CHATID = int(os.getenv('CHATID'))
MYTOKEN = os.getenv('MYTOKEN')
TZ = os.getenv('TZ', 'America/New_York')
INTERVAL = int(os.getenv('INTERVAL', 120))
SENSOR_PIN = int(os.getenv('SENSOR_PIN', 14))
AVG_THRESHOLD = float(os.getenv('AVG_THRESHOLD', 0.2))

# Optional
DEBUG = int(os.getenv('DEBUG', 0))

# --- Other Globals ---
READINGS = 1000000
SLICES = 4
RAMP_UP_READINGS = 4
RAMP_DOWN_READINGS = 4

VER = "1.16"
USER_AGENT = f"vibinator.py/{VER}"

# Setup logger
logger = logging.getLogger()
ch = logging.StreamHandler()
if DEBUG:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s',
                              datefmt='[%d %b %Y %H:%M:%S %Z]')
ch.setFormatter(formatter)
logger.addHandler(ch)


def send_notification(msg: str, chat_id: int, token: str) -> None:
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)
    logger.info("Telegram Group Message Sent")


def sensor_init(pin: int) -> None:
    RPi.GPIO.setwarnings(False)
    RPi.GPIO.setmode(RPi.GPIO.BCM)
    RPi.GPIO.setup(pin, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)


def take_reading(num_readings: int, pin: int) -> float:
    total_readings = 0
    for _ in range(num_readings):
        total_readings += RPi.GPIO.input(pin)
    return (total_readings / num_readings)


def main() -> None:
    sensor_init(SENSOR_PIN)
    logger.info(f"Startup: {USER_AGENT}")
    is_running = 0
    ramp_up = 0
    ramp_down = 0
    while True:
        slice_sum = 0
        for i in range(SLICES):
            result = take_reading(READINGS, SENSOR_PIN)
            if (DEBUG):
                logger.debug(f"Slice result was: {result}")
            slice_sum += result
            sleep(INTERVAL/SLICES)
        slice_avg = slice_sum / SLICES
        if (DEBUG):
            logger.debug(f"slice_avg was: {slice_avg}")
        if is_running == 0:
            if slice_avg >= AVG_THRESHOLD:
                ramp_up += 1
                if ramp_up > RAMP_UP_READINGS:
                    is_running = 1
                    logger.info(f"Transition to running: {slice_avg}")
                else:
                    logger.debug(f"Tracking Non-Zero Readings: {ramp_up}")
            else:
                ramp_up = 0
                if (DEBUG):
                    logger.debug(f"Remains stopped: {slice_avg}")
        else:
            if slice_avg < AVG_THRESHOLD:
                ramp_down += 1
                if ramp_down > RAMP_DOWN_READINGS:
                    is_running = 0
                    logger.info("Transition to stopped")
                    now = strftime("%B %d, %Y at %H:%M")
                    notification_text = f"Dryer finished on {now}. Go switch out the laundry!"  # noqa: E501
                    send_notification(notification_text, CHATID, MYTOKEN)
                else:
                    logger.debug(f"Tracking Zero Readings: {ramp_down}")
            else:
                ramp_down = 0
                if (DEBUG):
                    logger.debug(f"Remains running: {slice_avg}")


if __name__ == "__main__":
    main()
