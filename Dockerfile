FROM python:3.11

RUN apt-get update && \
    apt install python3-poetry -y

RUN mkdir -p /app/src

COPY . /app/src

WORKDIR /app/src

VOLUME /logs

VOLUME /data

RUN poetry install

CMD ["python","main.py"]