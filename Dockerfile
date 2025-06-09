FROM ubuntu:noble-20250529

ARG TZ=America/New_York
RUN apt update && DEBIAN_FRONTEND=noninteractive apt -yq install python3-gpiozero python3-requests python3-python-telegram-bot

RUN mkdir /app

COPY ./vibinator.py /app
RUN chmod 755 /app/vibinator.py

ENTRYPOINT [ "python3", "-u", "/app/vibinator.py" ]
