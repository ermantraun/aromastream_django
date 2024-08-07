
FROM postgres:15

RUN apt-get update && apt-get install -y \
    nano \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN echo "listen_addresses='*'" >> /usr/share/postgresql/postgresql.conf.sample && \
    echo "host all all 0.0.0.0/0 md5" >> /usr/share/postgresql/pg_hba.conf.sample

COPY init-db.sh /docker-entrypoint-initdb.d/

RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh

ENV POSTGRES_USER=django
ENV POSTGRES_PASSWORD=8995
ENV POSTGRES_DB=django
CMD ["postgres"]
