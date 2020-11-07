#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import requests

IFTTTKEY = 'your-ifttt-webhook-key'
IFTTTWEBHOOK = 'your-ifttt-webhook-name'
INTERVAL = 15
SENSOR_PIN = 14
READINGS = 1000000
MAX_ZERO_READINGS = 20


VER = "0.1"
USER_AGENT = "vibinator.py/" + VER

def triggerWebHook():
    webHookURL = "/".join(
        ("https://maker.ifttt.com/trigger",
        IFTTTWEBHOOK,
        "with/key",
        IFTTTKEY)
    )
    headers = {'User-Agent': USER_AGENT }
    r = requests.get(webHookURL, headers=headers)
    writeLogEntry("IFTTT Response", r.text)

def writeLogEntry(message, status):
    print(time.strftime("[%d %b %Y %H:%M:%S %Z]", time.localtime()) + " {}: {}".format(message, status))

def main():
    writeLogEntry('Initiated', '')
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    IS_RUNNING = 0
    ZERO_READ = 0

    while True:
        agg = 0
        for i in range(READINGS):
            agg += GPIO.input(SENSOR_PIN)
        avg = agg / READINGS
        if IS_RUNNING == 0:
            if avg > 0:
                IS_RUNNING = 1
                writeLogEntry('Transition to running', avg)
            else:
                writeLogEntry('Remains stopped', avg)
        else:
            if avg == 0:
                ZERO_READ += 1
                if ZERO_READ > MAX_ZERO_READINGS:
                    IS_RUNNING = 0
                    writeLogEntry('Transition to stopped', '')
                    triggerWebHook()
                else:
                    writeLogEntry('Tracking Zero Readings', ZERO_READ)
            else:
                ZERO_READ = 0
                writeLogEntry('Remains running', avg)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
