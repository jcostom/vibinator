FROM python:slim

ENV TZ=America/New_York

RUN apt update && apt -yq install gcc make

RUN pip install requests && pip install RPi.GPIO

RUN mkdir /app

COPY ./vibinator.py /app
RUN chmod 755 /app/vibinator.py

ENTRYPOINT [ "python3", "-u", "/app/vibinator.py" ]
