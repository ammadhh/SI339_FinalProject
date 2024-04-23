"""User db api."""
import flask
import coolmedia
from coolmedia.util.helper import password_hash


def auth_user():
    """Authenticate user."""
    users_tb = UsersPortal()

    if (
        not flask.request.authorization
        or "username" not in flask.request.authorization
        or "password" not in flask.request.authorization
    ) and "username" not in flask.session:
        return ""
    if "username" in flask.session:
        return flask.session["username"]
    username = flask.request.authorization["username"]
    password = flask.request.authorization["password"]
    if not users_tb.verify_password(username, password):
        return ""
    return username


class UsersPortal:
    """Portal to users DB."""

    # username
    # fullname
    # email
    # filename
    # password
    # salt
    # created
    def __init__(self):
        """Initialize function."""
        self.connection = coolmedia.model.get_db()

    def all_username(self, logname: str) -> list:
        """Return all username except logname."""
        cur = self.connection.execute(
            "SELECT username "
            "FROM users "
            "WHERE username != ?", (logname,)
        )
        usernames = cur.fetchall()
        return [u["username"] for u in usernames]

    def create(self, row: dict):
        """Store newly created account."""
        password, username = row["password"], row["username"]
        fullname, email = row["fullname"], row["email"]
        filename = row["filename"]
        hashed_password = password_hash(password)
        self.connection.execute(
            "INSERT INTO users "
            "(username, fullname, email, filename, password) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, fullname, email, filename, hashed_password)
            )

    def update(self, username: str, fullname: str, email: str, filename=None):
        """Update user profile."""
        self.connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ? ",
            (fullname, email, username),
        )

        if filename:
            self.connection.execute(
                "UPDATE users "
                "SET filename = ? "
                "WHERE username = ? ",
                (filename, username),
            )

    def update_password(self, username: str, new_password: str):
        """Update username password."""
        self.connection.execute(
            "UPDATE users "
            "SET password = ? "
            "WHERE username = ? ",
            (new_password, username),
        )

    def delete(self, username: str):
        """Delete username account."""
        self.connection.execute(
            "DELETE FROM users "
            "WHERE username = ?", (username,)
        )

    def get_user_img(self, username: str) -> str:
        """Get img url for username."""
        cur = self.connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?", (username,)
        )

        return cur.fetchone()["filename"]

    def get_user_fullname(self, username: str) -> str:
        """Get fullname of username."""
        cur = self.connection.execute(
            "SELECT fullname "
            "FROM users "
            "WHERE username = ?", (username,)
        )

        return cur.fetchone()["fullname"]

    def get_user_email(self, username: str) -> str:
        """Get email of username."""
        cur = self.connection.execute(
            "SELECT email "
            "FROM users "
            "WHERE username = ?", (username,)
        )

        return cur.fetchone()["email"]

    def verify_user(self, username: str) -> bool:
        """Verify that the user exists in database."""
        cur = self.connection.execute(
            "SELECT fullname "
            "FROM users "
            "WHERE username = ?", (username,)
        )

        return cur.fetchone() is not None

    def verify_password(self, username: str, password: str) -> bool:
        """
        Verify whether the password is correct.

        Return False if there is no username or password does not match.
        """
        cur = self.connection.execute(
            "SELECT password "
            "FROM users "
            "WHERE username = ?", (username,)
        )

        result = cur.fetchone()
        if not result:
            return False

        stored_password = result["password"]
        salt = stored_password.split("$")[1]
        hashed_password = password_hash(password, salt)

        if hashed_password != stored_password:
            return False
        return True
