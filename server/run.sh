#! /usr/bin/env bash

OH_ENV=production .venv/bin/uvicorn --proxy-headers main:app &

pid=$!
echo "$pid" > process.pid

# .venv/bin/uvicorn --proxy-headers --forwarded-allow-ips='*' --uds /run/uvicorn/hemeroteca-oberta.sock main:app
