"""Helper functions for other files."""
import uuid
import hashlib
import pathlib
import arrow
import flask
import coolmedia


def get_target():
    """Get the target specified in the request."""
    target = flask.request.args.get('target')
    if not target:
        target = "/"
    return target


def check_filename(filename):
    """Check if filename is empty."""
    if not filename:
        flask.abort(400)


def get_time(created: str):
    """Return a humanized time."""
    time = arrow.get(created, 'YYYY-MM-DD HH:mm:ss')
    return time.humanize()


def get_time_int(created: str) -> int:
    """Return a time in int form."""
    time = arrow.get(created, 'YYYY-MM-DD HH:mm:ss')
    return int(time.timestamp())


def password_hash(password: str, salt=None) -> str:
    """Hashe a password."""
    algorithm = 'sha512'
    if not salt:
        salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    hash_digest = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, hash_digest])
    return password_db_string


def store_file(filename: str, fileobj) -> str:
    """Store an uploaded file in the uploads folder."""
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    path = coolmedia.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    return uuid_basename
