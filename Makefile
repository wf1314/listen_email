#!/usr/bin/bash

build:
	docker build -f ./Dockerfile -t mail:v1 .

run:
	docker-compose up -d
