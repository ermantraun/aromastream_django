
FROM python:3.12.4-bookworm

RUN apt-get update && \
    apt-get clean

USER root

COPY . ./aromastream_django

WORKDIR /aromastream_django

RUN pip install -r requirements.txt


WORKDIR /aromastream_django/api

CMD ["bash"]
