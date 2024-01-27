FROM postgres

COPY init.sql /docker-entrypoint-initdb.d/
ENV POSTGRES_PASSWORD=12345678

# RUN  psql postgresql://postgres:12345678@localhost:5432
# RUN  create database fastapi_db;
