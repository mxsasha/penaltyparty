import os

from . import *  # noqa: F403

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
hostname = os.getenv("HOSTNAME", "")
ALLOWED_HOSTS = [hostname, "www." + hostname]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [f"https://{hostname}", f"https://www.{hostname}"]

ADMINS = [("", "django@s42.re")]

DEFAULT_FROM_EMAIL = os.getenv("EMAIL_FROM")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_SUBJECT_PREFIX = os.getenv(f"[{hostname}]")
EMAIL_USE_TLS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": "host.docker.internal",
        "PORT": "5432",
        "CONN_MAX_AGE": None,
    }
}
