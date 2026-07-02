FROM python:3.11-alpine

RUN apk add --no-cache bash

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x /app/run.sh

CMD ["/bin/bash", "/app/run.sh"]