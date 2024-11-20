# pull official base image
FROM python:3.12.7-alpine

RUN pip install poetry

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE penaltyparty.settings.docker

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

CMD ["./docker-startup.sh"]
