#!/usr/bin/env python3

import asyncio
import logging
import os
import telegram
import RPi.GPIO
from time import sleep, strftime

# --- To be passed in to container ---
# Globals
CHATID = int(os.getenv('CHATID'))
MYTOKEN = os.getenv('MYTOKEN')
TZ = os.getenv('TZ', 'America/New_York')
SENSOR_PIN = int(os.getenv('SENSOR_PIN', 14))
INTERVAL = int(os.getenv('INTERVAL', 120))
READINGS = int(os.getenv('READINGS', 1000000))
AVG_THRESHOLD = float(os.getenv('AVG_THRESHOLD', 0.2))
SLICES = int(os.getenv('SLICES', 4))
RAMP_UP_READINGS = int(os.getenv('RAMP_UP_READINGS', 4))
RAMP_DOWN_READINGS = int(os.getenv('RAMP_DOWN_READINGS', 4))


# Optional
DEBUG = int(os.getenv('DEBUG', 0))

VER = '2.3.1'
USER_AGENT = f"vibinator.py/{VER}"

# Setup logger
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
logging.basicConfig(level=LOG_LEVEL,
                    format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt='[%d %b %Y %H:%M:%S %Z]')
logger = logging.getLogger()


async def send_notification(msg: str, chat_id: int, token: str) -> None:
    bot = telegram.Bot(token=token)
    await bot.sendMessage(chat_id=chat_id, text=msg)
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
            DEBUG and logger.debug(f"Slice result was: {result}")
            slice_sum += result
            sleep(INTERVAL/SLICES)
        slice_avg = slice_sum / SLICES
        DEBUG and logger.debug(f"slice_avg was: {slice_avg}")
        if is_running == 0:
            if slice_avg >= AVG_THRESHOLD:
                ramp_up += 1
                if ramp_up > RAMP_UP_READINGS:
                    is_running = 1
                    logger.info(f"Transition to running: {slice_avg}")
                else:
                    DEBUG and logger.debug(f"Tracking Non-Zero Readings: {ramp_up}")  # noqa: E501
            else:
                ramp_up = 0
                DEBUG and logger.debug(f"Remains stopped: {slice_avg}")
        else:
            if slice_avg < AVG_THRESHOLD:
                ramp_down += 1
                if ramp_down > RAMP_DOWN_READINGS:
                    is_running = 0
                    logger.info("Transition to stopped")
                    now = strftime("%B %d, %Y at %H:%M")
                    notification_text = f"Dryer finished on {now}. Go switch out the laundry!"  # noqa: E501
                    asyncio.run(send_notification(notification_text, CHATID, MYTOKEN))  # noqa: E501
                else:
                    DEBUG and logger.debug(f"Tracking Zero Readings: {ramp_down}")  # noqa: E501
            else:
                ramp_down = 0
                DEBUG and logger.debug(f"Remains running: {slice_avg}")


if __name__ == "__main__":
    main()
