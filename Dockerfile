FROM python:3.10-slim

SHELL ["/bin/bash", "-c"]
WORKDIR /app

COPY src/. .env requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get -y update
RUN apt-get -y install curl


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


CMD ["uvicorn", "main:app", "--reload", "--port", "8000", "--host", "0.0.0.0"]
