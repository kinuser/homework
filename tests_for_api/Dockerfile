FROM python:3.10-slim

SHELL ["/bin/bash", "-c"]
WORKDIR /tests

COPY tests_api/ requirements.txt ./ 
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


CMD ["pytest", "-sv", "."]
