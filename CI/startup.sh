#!/bin/ash
apk update && apk add alpine-conf
setup-timezone -z Canada/Pacific

apk update && apk add gcc

apk update && apk add musl-dev && apk add git

pip install --no-cache-dir -r requirements.txt

python main.py