# pull official base image
FROM python:3.12.7-alpine AS base

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH}

RUN pip install poetry

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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

FROM base AS development
# install postgresql related packages
ENV DJANGO_SETTINGS_MODULE penaltyparty.settings.dev
RUN apk update && apk add bash && apk add dpkg
RUN apk add \
  --no-cache \
  --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
  postgresql18


FROM base AS production
ENV DJANGO_SETTINGS_MODULE penaltyparty.settings.docker
CMD ["./docker-startup.sh"]