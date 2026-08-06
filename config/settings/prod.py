# flake8: noqa: F405
"""Production settings: imports everything from base.py, then applies prod overrides."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa F401

# Note: it is recommended to use the "DEBUG" environment variable to override this value in base.py.
# A future release may remove it from here.
DEBUG = False

# Production requires a PostgreSQL database via DATABASE_URL. There is no SQLite
# fallback here: fail loudly at startup if it is missing or points elsewhere.
if "DATABASE_URL" not in env:
    raise ImproperlyConfigured("DATABASE_URL must be set in production.")

DATABASES = {"default": env.db("DATABASE_URL")}

if "postgresql" not in str(DATABASES["default"].get("ENGINE", "")):
    raise ImproperlyConfigured("Production requires a PostgreSQL DATABASE_URL.")

# Serve static files directly from the app via WhiteNoise (no separate web server / CDN required).
# Insert the middleware immediately after SecurityMiddleware, per WhiteNoise's docs.
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)
# Compress static files at collectstatic time. We avoid the *Manifest* variant because assets
# referenced inside built CSS (fonts/images) can break under hashed-manifest storage.
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedStaticFilesStorage"

# fix ssl mixed content issues
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django security checklist settings.
# More details here: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security settings
# Without uncommenting the lines below, you will get security warnings when running ./manage.py check --deploy
# https://docs.djangoproject.com/en/stable/ref/middleware/#http-strict-transport-security

# # Increase this number once you're confident everything works https://stackoverflow.com/a/49168623/8207
# SECURE_HSTS_SECONDS = 60
# # Uncomment these two lines if you are sure that you don't host any subdomains over HTTP.
# # You will get security warnings if you don't do this.
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

USE_HTTPS_IN_ABSOLUTE_URLS = True

# If you don't want to use environment variables to set production hosts you can add them here
# ALLOWED_HOSTS = ["example.com"]

# Email is configured in base.py: outside DEBUG it sends over SMTP via Resend, so all this
# environment needs is RESEND_API_KEY (plus a DEFAULT_FROM_EMAIL on a verified domain).
# Point EMAIL_HOST / EMAIL_PORT / EMAIL_HOST_USER at another provider to switch.

ADMINS = ["achinga.chris@gmail.com"]
