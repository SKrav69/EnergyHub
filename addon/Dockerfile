FROM python:3.11-alpine

ARG BUILD_VERSION
ARG BUILD_ARCH

ENV ENERGYHUB_VERSION="${BUILD_VERSION}"

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}"

RUN apk add --no-cache bash

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

RUN python3 -m unittest discover -s tests -v

RUN chmod +x /app/run.sh

CMD ["/bin/bash", "/app/run.sh"]