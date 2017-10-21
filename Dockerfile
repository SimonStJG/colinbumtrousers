FROM python:3.6

MAINTAINER SimonStJG <Simon.StJG@gmail.com>

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt
COPY ./client_secret.json /client_secret.json
COPY ./src /src

CMD python3 src/colin.py

