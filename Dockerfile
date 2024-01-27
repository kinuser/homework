FROM python

SHELL ["/bin/bash", "-c"]
WORKDIR /app

COPY src/. .env pytest.ini requirements.txt ./
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


CMD ["uvicorn", "main:app", "--reload", "--port", "8000", "--host", "0.0.0.0"]



