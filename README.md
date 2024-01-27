# Social network

## Env

Директория env в корне отвечает за разделение окружений
/env/local - локальное окружение, предназначено для развертывания разработчиками на локальных машинах
/env/dev - окружение development стенда

...

И так далее

## Запуск проекта в Docker (локальное окружение)

```bash
cp env/local/.env.example ./.env
cd env/local/docker
docker compose up -d --build
```

После запуска композа - приложение будет доступно по порту 8000

## Запуск проекта локально

```bash
python3.10 -m venv venv
source venv/bin/activate

# run migrations
python manage.py migrate

python manage.py runserver

# generate openapi
./manage.py spectacular --color --file schema.yml
```

OpenApi спецификацию предполагается отображать при помощи плагинов IDE, либо в отдельном контейнере, если IDE не поддерживает плагины для openapi

```bash
docker run -p 80:8080 -e SWAGGER_JSON=/schema.yml -v ${PWD}/schema.yml:/schema.yml swaggerapi/swagger-ui
```

## Тесты

Запуск тестов

```bash
./manage.py test users/tests
```

## Auth

Для авторизации используется JWT

Все авторизованные запросы подписываются HTTP заголовком:

```HTTP
Authorization: Bearer <token>
```

```python
 # вот этот декоратор используется в качестве middleware 
 # для валидации JWT токена и получения данных пользователя
 # все эндпоинты, требующие авторизации - обернуты в этот декоратор
def jwt_auth_check(view_function):
    ...
```

## Запросы

Добавление в друзья реализовано по принципу подписок (что-то среднее между друзьями и подписками - как в ВК)

Для пользователя другом считается такой пользователь, который просто имеет с ним взаимную подписку

У каждой подписки есть признак просмотренности. Если подписка не просмотрена - значит есть входящий (если подписались на меня) или исходящий (если наоборот - я как пользователь подписался на кого-то)

Все запросы для подписок завязаны на username
