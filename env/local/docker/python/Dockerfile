FROM python:3.10.12
COPY ./friends_network/requirements.txt /project/
RUN pip install --no-cache-dir --upgrade -r /project/requirements.txt
COPY ./friends_network /project
WORKDIR /project
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000