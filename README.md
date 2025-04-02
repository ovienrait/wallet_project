# Wallet Project

## Описание

Этот проект представляет собой реализацию REST API приложения для работы с моделью Wallet.<br>
Приложение может принимать и обрабатывать следующие запросы:<br>
GET api/v1/wallets/<wallet_uuid> - получение баланса кошелька<br>
POST api/v1/wallets/<wallet_uuid>/operation - проведение операций с кошельком

### Стек технологий

* `Python`
* `Django REST Framework`
* `Django ORM`
* `PostgreSQL`
* `Pytest`
* `Docker`
* `Docker Compose`

### Установка и запуск

1. Создайте локальную копию проекта
```
git clone https://github.com/ovienrait/wallet_project.git
```
2. Перейдите в рабочую директорию
```
cd wallet_project
```
3. Запустите проект
```
docker compose up
```
В процессе запуска будет скачан образ для базы данных и будет собран образ для самого приложения, из которых будет поднята система контейнеров, будут установлены зависимости необходимые для работы проекта, автоматически применятся миграции и загрузятся фикстуры для базы данных, начнется тестирование, по окончании которого будет запущен сервер с работающим приложением.

 <br>

Документация к API с детальным описанием эндпоинтов и возможностью их тестирования будет доступна по адресу:
```
http://localhost:8000/api/docs
```

Так как это тестовое задание, файл <kbd>.env</kbd> загружен в репозиторий для быстрого запуска проекта.

## Контакты

Artem Maksimov - [@ovienrait](https://t.me/ovienrait) - [nirendsound@gmail.com](https://nirendsound@gmail.com)

Project Link: [Wallet Project](https://github.com/ovienrait/wallet_project.git)
