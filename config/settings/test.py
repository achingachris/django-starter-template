"""Test settings: everything from base.py, tuned so the suite runs fast and offline.

Selected by `make test` and CI (see Makefile and .github/workflows/tests.yml).
"""

from .base import *  # noqa: F403

# MD5 is intentionally weak here: password hashing dominates runtime for any test that
# creates users, and test databases hold no real credentials.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Keep outbound mail in memory (django.core.mail.outbox) — tests never print or send anything.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
