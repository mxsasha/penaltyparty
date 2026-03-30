from . import *  # noqa: F403

SECRET_KEY = "django-insecure-xj9qpi$1i6y1bx)0s!36-iok(3gs3h80*g4g)^9_dp9d-)#_6="
DEBUG = True
ALLOWED_HOSTS = []

ADMINS = [("", "django@s42.re")]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "null@example.com"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": "dev_db",
        "PORT": "5432",
        "CONN_MAX_AGE": None,
    }
}

DEFAULT_TEST_GROUP_QUESTION_AMOUNT = 3