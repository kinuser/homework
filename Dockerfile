FROM python:3.10-slim

SHELL ["/bin/bash", "-c"]
WORKDIR /app

COPY src/. .env requirements.txt startup.sh ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get -y update
RUN apt-get -y install curl
RUN chmod +x ./startup.sh

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

CMD ["/app/startup.sh"]
