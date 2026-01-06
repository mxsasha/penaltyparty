# pull official base image
FROM python:3.12.7-alpine

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH}

RUN pip install poetry
# install postgresql related packages
RUN apk update && apk add bash && apk add dpkg
RUN apk add \
  --no-cache \
  --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
  postgresql18

# set default password for postgres user
RUN echo "password" > passwd postgres

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE penaltyparty.settings.dev

# create the app directory - and switch to it
RUN mkdir -p /app
WORKDIR /app

# copy project
COPY . /app/

# install dependencies
RUN /bin/true\
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction \
    && rm -rf /root/.cache/pypoetry

RUN python ./manage.py collectstatic --noinput

# expose port 8000
EXPOSE 8000