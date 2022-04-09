#!/usr/bin/env python3

import os
import logging
from time import sleep, strftime
import telegram
import RPi.GPIO

# Configurable
CHATID = int(os.getenv('CHATID'))
MYTOKEN = os.getenv('MYTOKEN')
TZ = os.getenv('TZ', 'America/New_York')
INTERVAL = int(os.getenv('INTERVAL', 120))
SENSOR_PIN = int(os.getenv('SENSOR_PIN', 14))
AVG_THRESHOLD = float(os.getenv('AVG_THRESHOLD', 0.2))
DEBUG = int(os.getenv('DEBUG', 0))

# Static
READINGS = 1000000
SLICES = 4
RAMP_UP_READINGS = 4
RAMP_DOWN_READINGS = 4
VER = "1.6"
USER_AGENT = "/".join(['vibinator.py', VER])

# Setup loggers
inflogger = logging.getLogger()
inflogger.setLevel(logging.INFO)
infch = logging.StreamHandler()
infch.setLevel(logging.INFO)

deblogger = logging.getLogger()
deblogger.setLevel(logging.DEBUG)
debch = logging.StreamHandler()
debch.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s',
                              datefmt='[%d %b %Y %H:%M:%S %Z]')

infch.setFormatter(formatter)
debch.setFormatter(formatter)

inflogger.addHandler(infch)
deblogger.addHandler(debch)


def sendNotification(msg, chat_id, token):
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)
    inflogger.info("Telegram Group Message Sent")


def sensorInit(pin):
    RPi.GPIO.setwarnings(False)
    RPi.GPIO.setmode(RPi.GPIO.BCM)
    RPi.GPIO.setup(pin, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)


def takeReading(numReadings, pin):
    totalReadings = 0
    for i in range(numReadings):
        totalReadings += RPi.GPIO.input(pin)
    return(totalReadings / numReadings)


def main():
    sensorInit(SENSOR_PIN)
    inflogger.info("Startup: {}".format(USER_AGENT))
    IS_RUNNING = 0
    RAMP_UP = 0
    RAMP_DOWN = 0
    while True:
        # intervals are 120s, do 4 slices
        sliceSum = 0
        for i in range(SLICES):
            result = takeReading(READINGS, SENSOR_PIN)
            if (DEBUG):
                deblogger.debug("Slice result was: {}".format(result))
            sliceSum += result
            sleep(INTERVAL/SLICES)
        sliceAvg = sliceSum / SLICES
        if (DEBUG):
            deblogger.debug("sliceAvg was: {}".format(sliceAvg))
        if IS_RUNNING == 0:
            if sliceAvg >= AVG_THRESHOLD:
                RAMP_UP += 1
                if RAMP_UP > RAMP_UP_READINGS:
                    IS_RUNNING = 1
                    inflogger.info("Transition to running: {}".format(sliceAvg))  # noqa E501
                else:
                    inflogger.info("Tracking Non-Zero Readings: {}".format(RAMP_UP)) # noqa E501
            else:
                RAMP_UP = 0
                inflogger.info("Remains stopped: {}".format(sliceAvg))
        else:
            if sliceAvg < AVG_THRESHOLD:
                RAMP_DOWN += 1
                if RAMP_DOWN > RAMP_DOWN_READINGS:
                    IS_RUNNING = 0
                    inflogger.info("Transition to stopped")
                    notificationText = "".join(
                        ("Dryer finished on ",
                         strftime("%B %d, %Y at %H:%M"),
                         ". Go switch out the laundry!")
                    )
                    sendNotification(notificationText, CHATID, MYTOKEN)
                else:
                    inflogger.info("Tracking Zero Readings: {}".format(RAMP_DOWN)) # noqa E501
            else:
                RAMP_DOWN = 0
                inflogger.info("Remains running: {}".format(sliceAvg))


if __name__ == "__main__":
    main()
