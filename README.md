# FastAPI сервис по сокращению ссылок

## Запуск в detached режиме: 

`docker compose up --build -d`

## Описание проекта

* FastAPI
* POstgres
* Redis [не доделано]
* Docker compose
* Регистрация по принципам OAuth2 с токенами
* bcrypt хэширование паролей
* shortuuid генерация коротких ссылок с проверкой коллизий
* Запись статы поп редиректам в Postgres

## Endpoints

Root:
* GET `/` - root

Authentication:
* POST `/auth/get_token` - регистрация и запрос токена через request body
* POST `/auth/token` - регистрация и запрос токена через forms в доке
* POST `/auth/update_token` - обновить токен, если истек срок действия

Links:
* POST `/links/shorten` - сокращает длинный URL
* GET `/links/{short_code}` - редирект на длинный URL
* DELETE `/links/{short_code}` - удаляет короткий URL
* PUT `/links/{short_code}` - назначает новый длинный URL. Так мне показалось логичнее. Типа у пользователя меняется домен, а он хочет продолжать вести стату по старому короткому URL.
* GET `/links/{short_code}/stats` - подсчет количества переходов как пример сбора статистики

## Примеры запросов

Можно посмотреть в файле `tests/test.ipynb`

## Описание БД

![alt text](img/DB.png)

## Запуск тестов

Для запуска тестов из корневой папки проекта:

`pytest -v`

`locust -f ./tests/locustfile.py`

Результаты тестов в папке /tests/img