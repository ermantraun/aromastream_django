
FROM python:3.12.4-bookworm
USER root

RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean



COPY . ./aromastream_django
COPY ./api/configs/nginx.conf /etc/nginx/sites-available/nginx.conf
RUN ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/
RUN rm /etc/nginx/sites-enabled/default
RUN chmod +x /aromastream_django/api/configs/uwsgi_params

WORKDIR /aromastream_django


RUN pip install -r requirements.txt


WORKDIR /aromastream_django/api

CMD ["bash"]
