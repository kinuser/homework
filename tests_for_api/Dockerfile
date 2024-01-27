FROM python

SHELL ["/bin/bash", "-c"]
WORKDIR /tests

COPY tests_api/ requirements.txt ./ 
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV APP_HOST=localhost
ENV APP_PORT=8000


CMD ["pytest", "-sv", "."]
