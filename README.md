# DimaTech_test_case

Тестовое задание кампании DimaTech Ltd: асинхронное веб приложение в парадигме REST API

Нюансы: Убрал .env из гитигнора чтобы вы могли сбилдиться у себя

Способы запуска:
1)С докер композом:
docker compose up --build -d
2)Без докера:
uvicorn app.main:app --reload но не запустится потому что не подключится бд, но это в целом не нужно есть же докер.

Тестовая миграция: чтобы её провести нужно:
docker compose up --build -d Cбилдить проект
docker compose exec dimatech_integration alembic upgrade head запустить миграцию

Креды пользователей создаваемых этой миграцией:
Юзер:
test_user@example.com
123
Админ:
test_admin@example.com
123

Ссылка на сваггер: http://localhost:8080/docs
