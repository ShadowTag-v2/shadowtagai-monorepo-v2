#!/bin/bash
export PYTHONPATH=$PYTHONPATH:.
uvicorn apps.src.relay_server:app --host 0.0.0.0 --port 8080
