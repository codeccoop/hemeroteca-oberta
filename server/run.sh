#! /usr/bin/env bash

if [ -f process.pid ];
then
    kill $(cat process.pid)
fi

echo "Start running server"
OH_ENV=production nohup .venv/bin/uvicorn --proxy-headers main:app &>/dev/null &

pid=$!
echo "$pid" > process.pid
echo "Running server with PID $pid"

# .venv/bin/uvicorn --proxy-headers --forwarded-allow-ips='*' --uds /run/uvicorn/hemeroteca-oberta.sock main:app
