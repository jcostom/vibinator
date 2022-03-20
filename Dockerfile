FROM python:slim as builder

ENV TZ=America/New_York
RUN apt update && apt -yq install gcc make
RUN pip install python-telegram-bot && pip install RPi.GPIO

FROM python:slim

ENV TZ=America/New_York

COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/

RUN mkdir /app

COPY ./vibinator.py /app
RUN chmod 755 /app/vibinator.py

ENTRYPOINT [ "python3", "-u", "/app/vibinator.py" ]
