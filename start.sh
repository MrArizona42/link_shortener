#!/bin/sh
uvicorn app.main:app --host ${APP_HOST} --port ${APP_PORT} --reload=${APP_RELOAD} --workers=${APP_WORKERS}
