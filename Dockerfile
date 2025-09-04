FROM python:3.13.7-alpine

WORKDIR /app

COPY ./requirements.txt requirements.txt
COPY ./.env .env

COPY ./main.py main.py

RUN pip3 install -r requirements.txt

WORKDIR /app
CMD ["python", "main.py"]