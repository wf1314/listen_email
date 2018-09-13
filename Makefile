#!/usr/bin/bash

build:
	docker build -f ./Dockerfile -t email:v2 .

run:
	docker-compose up -d
