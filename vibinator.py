#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import requests

IFTTTKEY = 'your-ifttt-webhook-key'
IFTTTWEBHOOK = 'your-ifttt-webhook-name'
INTERVAL = 300
SENSOR_PIN = 14
READINGS = 1000000
RAMP_UP_READINGS = 5
RAMP_DOWN_READINGS = 20
AVG_THRESHOLD = 0.3

VER = "0.5"
USER_AGENT = "vibinator.py/" + VER


def triggerWebHook():
    webHookURL = "/".join(
        ("https://maker.ifttt.com/trigger",
         IFTTTWEBHOOK,
         "with/key",
         IFTTTKEY)
    )
    headers = {'User-Agent': USER_AGENT}
    r = requests.get(webHookURL, headers=headers)
    writeLogEntry("IFTTT Response", r.text)


def writeLogEntry(message, status):
    print(time.strftime("[%d %b %Y %H:%M:%S %Z]",
          time.localtime()) + " {}: {}".format(message, status))


def main():
    writeLogEntry('Initiated', USER_AGENT)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    IS_RUNNING = 0
    RAMP_UP = 0
    RAMP_DOWN = 0

    while True:
        agg = 0
        for i in range(READINGS):
            agg += GPIO.input(SENSOR_PIN)
        avg = agg / READINGS
        if IS_RUNNING == 0:
            if avg >= AVG_THRESHOLD:
                RAMP_UP += 1
                if RAMP_UP > RAMP_UP_READINGS:
                    IS_RUNNING = 1
                    writeLogEntry('Transition to running', avg)
                else:
                    writeLogEntry('Tracking Non-Zero Readings', RAMP_UP)
            else:
                RAMP_UP = 0
                writeLogEntry('Remains stopped', avg)
        else:
            if avg < AVG_THRESHOLD:
                RAMP_DOWN += 1
                if RAMP_DOWN > RAMP_DOWN_READINGS:
                    IS_RUNNING = 0
                    writeLogEntry('Transition to stopped', '')
                    triggerWebHook()
                else:
                    writeLogEntry('Tracking Zero Readings', RAMP_DOWN)
            else:
                RAMP_DOWN = 0
                writeLogEntry('Remains running', avg)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
