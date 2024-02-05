FROM python:3.10-slim

SHELL ["/bin/bash", "-c"]
WORKDIR /tests

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


CMD ["pytest", "-sv", "tests/"]
