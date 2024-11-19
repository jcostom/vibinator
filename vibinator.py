#!/usr/bin/env python3

import asyncio
import logging
import os
import json
import requests
import telegram
from gpiozero import LineSensor
from time import sleep, strftime

# --- To be passed in to container ---
# Globals
TZ = os.getenv('TZ', 'America/New_York')
SENSOR_PIN = int(os.getenv('SENSOR_PIN', 14))
INTERVAL = int(os.getenv('INTERVAL', 120))
READINGS = int(os.getenv('READINGS', 1000000))
AVG_THRESHOLD = float(os.getenv('AVG_THRESHOLD', 0.8))
SLICES = int(os.getenv('SLICES', 4))
RAMP_UP_READINGS = int(os.getenv('RAMP_UP_READINGS', 3))
RAMP_DOWN_READINGS = int(os.getenv('RAMP_DOWN_READINGS', 3))

# Optional
DEBUG = int(os.getenv('DEBUG', 0))

# Optional Vars for Notification Types
# Telegram
USE_TELEGRAM = int(os.getenv('USE_TELEGRAM', 0) or os.getenv('USETELEGRAM', 0))  # noqa E501
TELEGRAM_CHATID = int(os.getenv('TELEGRAM_CHATID', 0) or os.getenv('CHATID', 0))  # noqa E501
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'none') or os.getenv('MYTOKEN', 'none')  # noqa E501

# Pushover
USE_PUSHOVER = int(os.getenv('USE_PUSHOVER', 0) or os.getenv('USEPUSHOVER', 0))  # noqa E501
PUSHOVER_APP_TOKEN = os.getenv('PUSHOVER_APP_TOKEN')
PUSHOVER_USER_KEY = os.getenv('PUSHOVER_USER_KEY')

# Pushbullet
USE_PUSHBULLET = int(os.getenv('USE_PUSHBULLET', 0) or os.getenv('USEPUSHBULLET', 0))  # noqa E501
PUSHBULLET_APIKEY = os.getenv('PUSHBULLET_APIKEY')

# Alexa "Notify Me" - Add this Skill to your Alexa Account before you use this!
USE_ALEXA = int(os.getenv('USE_ALEXA', 0) or os.getenv('USEALEXA', 0))  # noqa E501
ALEXA_ACCESSCODE = os.getenv('ALEXA_ACCESSCODE')

# Other Globals
VER = '3.0.6'
USER_AGENT = f"vibinator.py/{VER}"

# Setup logger
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
logging.basicConfig(level=LOG_LEVEL,
                    format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt='[%d %b %Y %H:%M:%S %Z]')
logger = logging.getLogger()


async def send_telegram(msg: str, chat_id: int, token: str) -> None:
    bot = telegram.Bot(token=token)
    await bot.sendMessage(chat_id=chat_id, text=msg)
    logger.info("Telegram Group Message Sent")


def send_pushover(msg: str, token: str, user: str) -> requests.Response:
    url = "https://api.pushover.net/1/messages.json"
    data = {"token": token, "user": user, "message": msg}
    r = requests.post(url, data)
    logger.info('Pushover Message Sent')
    return r


def send_pushbullet(msg: str, apikey: str) -> requests.Response:
    url = "https://api.pushbullet.com/v2/pushes"
    data = {"type": "note", "body": msg}
    headers = {"Authorization": f"Bearer {apikey}", "Content-Type": "application/json"}  # noqa E501
    r = requests.post(url, data=json.dumps(data), headers=headers)
    logger.info('Pushbullet Message Sent')
    return r


def send_alexa(msg: str, access_code: str) -> requests.Response:
    url = "https://api.notifymyecho.com/v1/NotifyMe"
    data = {"notification": msg, "accessCode": access_code}
    r = requests.post(url, data=json.dumps(data))
    logger.info('Alexa Notification Sent')
    return r


def send_notifications(msg: str) -> None:
    if USE_TELEGRAM:
        asyncio.run(send_telegram(msg, TELEGRAM_CHATID, TELEGRAM_TOKEN))  # noqa E501
    if USE_PUSHOVER:
        send_pushover(msg, PUSHOVER_APP_TOKEN, PUSHOVER_USER_KEY)  # noqa E501
    if USE_PUSHBULLET:
        send_pushbullet(msg, PUSHBULLET_APIKEY)
    if USE_ALEXA:
        send_alexa(msg, ALEXA_ACCESSCODE)


def sensor_init(pin: int) -> LineSensor:
    s = LineSensor(pin=pin, pull_up=True)
    return s


def take_reading(num_readings: int, s: LineSensor) -> float:
    total_readings = 0
    for _ in range(num_readings):
        total_readings += s.value
    return (total_readings / num_readings)


def main() -> None:
    logger.info(f"Startup: {USER_AGENT}")
    sensor = sensor_init(SENSOR_PIN)
    is_running = 0
    ramp_up = 0
    ramp_down = 0
    while True:
        slice_sum = 0
        for i in range(SLICES):
            result = take_reading(READINGS, sensor)
            DEBUG and logger.debug(f"Slice result was: {result}")
            slice_sum += result
            sleep(INTERVAL / SLICES)
        slice_avg = slice_sum / SLICES
        DEBUG and logger.debug(f"slice_avg was: {slice_avg}")
        if is_running == 0:
            if slice_avg <= AVG_THRESHOLD:
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
            if slice_avg > AVG_THRESHOLD:
                ramp_down += 1
                if ramp_down > RAMP_DOWN_READINGS:
                    is_running = 0
                    logger.info("Transition to stopped")
                    now = strftime("%B %d, %Y at %H:%M")
                    notification_text = f"Dryer finished on {now}. Go switch out the laundry!"  # noqa: E501
                    send_notifications(notification_text)
                else:
                    DEBUG and logger.debug(f"Tracking Zero Readings: {ramp_down}")  # noqa: E501
            else:
                ramp_down = 0
                DEBUG and logger.debug(f"Remains running: {slice_avg}")


if __name__ == "__main__":
    main()
