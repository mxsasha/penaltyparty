from . import *  # noqa: F403

SECRET_KEY = "django-insecure-xj9qpi$1i6y1bx)0s!36-iok(3gs3h80*g4g)^9_dp9d-)#_6="
DEBUG = True
ALLOWED_HOSTS = []

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "null@example.com"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}
