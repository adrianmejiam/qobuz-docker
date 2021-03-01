FROM ubuntu:20.04

LABEL maintainer="Dehaeze Thomas <dehaeze.thomas@gmail.com>"

ENV \
  QOBUZNAME="" \
  QOBUZPASS="" \
  PUID="" \
  PGID=""

RUN \
  groupadd -g 1000 appuser && \
  useradd -r -u 1000 -g appuser appuser


RUN \
  echo "**** install runtime packages ****" && \
  apt-get update && \
  apt-get install -y --no-install-recommends \
      python3.4 \
      python3-pip

WORKDIR /app

RUN pip3 install --upgrade qobuz-dl CherryPy

COPY index.html index.html
COPY main.py main.py
ADD public public

CMD [ "python3", "main.py"]
