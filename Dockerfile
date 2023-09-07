FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG BOT_TOKEN
ENV BOT_TOKEN=${BOT_TOKEN}

ARG SQLITE_DB_PATH
ENV SQLITE_DB_PATH=${SQLITE_DB_PATH}

ARG LOGLEVEL
ENV LOGLEVEL=${LOGLEVEL}

ARG AUTHOR
ENV AUTHOR=${AUTHOR}

CMD ["python", "main.py"]
