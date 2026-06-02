FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=auth_db

COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 3306