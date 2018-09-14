#!/usr/bin/bash

build:
	docker build -f ./Dockerfile -t email:v2 .

run:
	docker-compose up -d

kill:
	ps -efww|grep -w 'tail -f /var/log/cron.log'|grep -v grep|cut -c 9-15|xargs kill -9
