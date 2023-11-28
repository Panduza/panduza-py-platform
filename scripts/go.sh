#!/bin/bash
docker build -t local/panduza-py-platform:latest .

cd /etc/panduza
docker compose run platformpy
