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
