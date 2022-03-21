#!/usr/bin/env python3

import os
import time
import telegram
import RPi.GPIO

# Configurable
CHATID = int(os.getenv('CHATID'))
MYTOKEN = os.getenv('MYTOKEN')
TZ = os.getenv('TZ', 'America/New_York')
INTERVAL = int(os.getenv('INTERVAL', 120))
SENSOR_PIN = int(os.getenv('SENSOR_PIN', 14))
AVG_THRESHOLD = float(os.getenv('AVG_THRESHOLD', 0.2))
LOGALL_ENV = os.getenv('LOGALL', False)
if LOGALL_ENV == "False":
    LOGALL = False
else:
    LOGALL = True

# Static
READINGS = 1000000
SLICES = 4
RAMP_UP_READINGS = 4
RAMP_DOWN_READINGS = 4
VER = "1.5.1"
USER_AGENT = "vibinator.py/" + VER


def sendNotification(msg, chat_id, token):
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)
    writeLogEntry("Telegram Group Message Sent", "")


def writeLogEntry(message, status):
    print(time.strftime("[%d %b %Y %H:%M:%S %Z]",
          time.localtime()) + " {}: {}".format(message, status))


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
    writeLogEntry('Initiated', USER_AGENT)
    IS_RUNNING = 0
    RAMP_UP = 0
    RAMP_DOWN = 0
    while True:
        # intervals are 120s, do 4 slices
        sliceSum = 0
        for i in range(SLICES):
            result = takeReading(READINGS, SENSOR_PIN)
            if (LOGALL):
                writeLogEntry('Slice result was', result)
            sliceSum += result
            time.sleep(INTERVAL/SLICES)
        sliceAvg = sliceSum / SLICES
        if (LOGALL):
            writeLogEntry('sliceAvg was', sliceAvg)
        if IS_RUNNING == 0:
            if sliceAvg >= AVG_THRESHOLD:
                RAMP_UP += 1
                if RAMP_UP > RAMP_UP_READINGS:
                    IS_RUNNING = 1
                    writeLogEntry('Transition to running', sliceAvg)
                else:
                    writeLogEntry('Tracking Non-Zero Readings', RAMP_UP)
            else:
                RAMP_UP = 0
                writeLogEntry('Remains stopped', sliceAvg)
        else:
            if sliceAvg < AVG_THRESHOLD:
                RAMP_DOWN += 1
                if RAMP_DOWN > RAMP_DOWN_READINGS:
                    IS_RUNNING = 0
                    writeLogEntry('Transition to stopped', '')
                    notificationText = "".join(
                        ("Dryer finished on ",
                         time.strftime("%B %d, %Y at %H:%M"),
                         ". Go switch out the laundry!")
                    )
                    sendNotification(notificationText, CHATID, MYTOKEN)
                else:
                    writeLogEntry('Tracking Zero Readings', RAMP_DOWN)
            else:
                RAMP_DOWN = 0
                writeLogEntry('Remains running', sliceAvg)


if __name__ == "__main__":
    main()
