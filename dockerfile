
FROM python:3.12.4-bookworm


RUN apt-get update && \
    apt-get install -y git postgresql postgresql-contrib libpq-dev && \
    apt-get clean

RUN git clone https://github.com/SkyAdam1/aromastream_django -b dev /aromastream_django


WORKDIR /aromastream_django/api


COPY requirements.txt .
RUN pip install -r requirements.txt


RUN echo "listen_addresses='*'" >> /etc/postgresql/15/main/postgresql.conf && \
    echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/15/main/pg_hba.conf

USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE DATABASE django;" && \
    psql --command "CREATE USER django WITH PASSWORD '8995';" && \
    psql --command "ALTER ROLE django SET client_encoding TO 'utf8';" && \
    psql --command "ALTER ROLE django SET default_transaction_isolation TO 'read committed';" && \
    psql --command "ALTER ROLE django SET timezone TO 'UTC';" && \
    psql --command "GRANT ALL ON DATABASE django TO django; " && \
    psql --command "ALTER DATABASE django OWNER TO django;" && \
    psql --command "GRANT USAGE, CREATE ON SCHEMA PUBLIC TO django; "


EXPOSE 5432 8000


USER root


CMD service postgresql start && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
