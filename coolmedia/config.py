"""Insta485 development configuration."""

import pathlib

# Root of this application,
# useful if it doesn't occupy an entire domain
APPLICATION_ROOT = "/"

# Secret key for encrypting cookies
SECRET_KEY = b"""Ebc\xd3\xbd\xf6j\x7f^
            !r\x80\x82k\xe5\xa9\xc5\xdd\xfe\xa8\x96\xf14\xe3"""
SESSION_COOKIE_NAME = "login"

# File Upload to var/uploads/
INSTA485_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = INSTA485_ROOT / "var" / "uploads"
TEMPLATE_FOLDER = INSTA485_ROOT / "coolmedia" / "templates"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/coolmedia.sqlite3
DATABASE_FILENAME = INSTA485_ROOT / "var" / "coolmedia.sqlite3"
