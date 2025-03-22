FROM python:3.12

# все импорты и комманды будут выполняться отсюда
WORKDIR /link_shortener

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./app ./app

CMD uvicorn app.main:app --host $APP_HOST --port $APP_PORT --workers $APP_WORKERS
