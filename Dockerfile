FROM python:3.10

RUN mkdir -p /src

COPY . /src

WORKDIR /src

VOLUME /logs

VOLUME /data

RUN pip install -r requirements.txt

CMD ["python","main.py"]