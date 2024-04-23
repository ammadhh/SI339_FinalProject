"""Insta485 Account view."""
import pathlib
import os
import flask
import coolmedia
from coolmedia.util import PostsPortal, UsersPortal
from coolmedia.util import password_hash, store_file, get_target, \
    check_filename


def login_helper(users_tb: UsersPortal):
    """Login helper."""
    username = flask.request.form.get("username")
    psw = flask.request.form.get("password")
    if not username or not psw:
        flask.abort(400)

    if not users_tb.verify_password(username, psw):
        return flask.abort(403)

    flask.session["username"] = flask.request.form["username"]

    return flask.redirect(get_target())


def create_helper(users_tb: UsersPortal):
    """Create helper."""
    if "file" not in flask.request.files:
        return flask.abort(400)
    fileobj = flask.request.files["file"]
    check_filename(fileobj.name)
    fullname = flask.request.form.get("fullname")
    username = flask.request.form.get("username")
    email = flask.request.form.get("email")
    psw = flask.request.form.get("password")
    if not fullname or not username or not email or not psw:
        return flask.abort(400)

    if users_tb.verify_user(username):
        return flask.abort(409)

    users_tb.create(
        {
            "filename": store_file(fileobj.name, fileobj),
            "username": username,
            "fullname": fullname,
            "email": email,
            "password": psw,
        }
    )

    flask.session["username"] = flask.request.form["username"]
    return flask.redirect(get_target())


def delete_helper(users_tb: UsersPortal):
    """Delete user."""
    if "username" not in flask.session:
        return flask.abort(403)

    file_list = []
    logname = flask.session["username"]

    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    # if not users_tb.verify_user(logname):
    #     flask.abort(403)

    posts_tb = PostsPortal()
    post_list = posts_tb.get_post_list(logname)
    for post in post_list:
        file_list.append(
            coolmedia.app.config["UPLOAD_FOLDER"] / post["filename"]
            )
    file_list.append(
        coolmedia.app.config["UPLOAD_FOLDER"] / users_tb.get_user_img(logname)
    )

    for file in file_list:
        if os.path.exists(file):
            os.remove(file)

    users_tb.delete(logname)
    flask.session.clear()
    return flask.redirect(get_target())


def edit_helper(users_tb: UsersPortal):
    """Edit user profile."""
    if "username" not in flask.session:
        return flask.abort(403)
    logname = flask.session["username"]

    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    fullname = flask.request.form.get("fullname")
    email = flask.request.form.get("email")
    if not fullname or not email:
        return flask.abort(400)

    # if not users_tb.verify_user(logname):
    #     flask.abort(403)

    uuid_basename = None
    if "file" in flask.request.files:
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        if filename:
            uuid_basename = store_file(filename, fileobj)
            # delete old img
            upload_folder = coolmedia.app.config["UPLOAD_FOLDER"]
            old_img = upload_folder / users_tb.get_user_img(logname)
            if os.path.exists(old_img):
                os.remove(old_img)

    users_tb.update(logname, fullname, email, uuid_basename)
    return flask.redirect(get_target())


def update_password_helper(users_tb: UsersPortal):
    """Update user password."""
    if "username" not in flask.session:
        return flask.abort(403)

    logname = flask.session["username"]

    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    psw = flask.request.form.get("password")
    new_password1 = flask.request.form.get("new_password1")
    new_password2 = flask.request.form.get("new_password2")

    # if not users_tb.verify_user(logname):
    #     flask.abort(403)

    if not psw or not new_password1 or not new_password2:
        return flask.abort(400)

    if not users_tb.verify_password(logname, psw):
        return flask.abort(403)

    if new_password1 != new_password2:
        return flask.abort(401)

    new_password = password_hash(new_password1)

    users_tb.update_password(logname, new_password)
    return flask.redirect(get_target())


@coolmedia.app.route("/accounts/", methods=["POST"])
def handle_account_post():
    """Handle post methods for /accounts/ URL."""
    users_tb = UsersPortal()
    operation = flask.request.form.get("operation")

    result = None
    if operation == "login":
        result = login_helper(users_tb)

    elif operation == "create":
        result = create_helper(users_tb)

    elif operation == "delete":
        result = delete_helper(users_tb)

    elif operation == "edit_account":
        result = edit_helper(users_tb)

    elif operation == "update_password":
        result = update_password_helper(users_tb)

    return result


@coolmedia.app.route("/accounts/create/", methods=["GET"])
def get_account_create():
    """Create a new account."""
    if "username" in flask.session:
        return flask.redirect("/accounts/edit/")
    return flask.render_template("account_create.html")


@coolmedia.app.route("/accounts/logout/", methods=["POST"])
def logout():
    """Logout of Insta485."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))
    flask.session.clear()
    return flask.redirect(flask.url_for("login"))


@coolmedia.app.route("/accounts/login/", methods=["GET"])
def login():
    """Login to your account."""
    if "username" in flask.session:
        return flask.redirect(flask.url_for("show_index"))
    return flask.render_template("account_login.html")


@coolmedia.app.route("/accounts/delete/", methods=["GET"])
def delete():
    """Delete an account."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))
    logname = flask.session["username"]
    users_tb = UsersPortal()
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    context = {"logname": logname}
    return flask.render_template("account_delete.html", **context)


@coolmedia.app.route("/accounts/edit/", methods=["GET"])
def edit():
    """Edit an account."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    logname = flask.session["username"]

    users_tb = UsersPortal()
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    uploads_folder = pathlib.Path("/uploads/")

    context = {
        "logname": logname,
        "logname_img_url": uploads_folder / users_tb.get_user_img(logname),
        "fullname": users_tb.get_user_fullname(logname),
        "email": users_tb.get_user_email(logname),
    }

    return flask.render_template("account_edit.html", **context)


@coolmedia.app.route("/accounts/password/", methods=["GET"])
def password():
    """Create a new password."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    logname = flask.session["username"]
    users_tb = UsersPortal()
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    context = {
        "logname": logname,
    }

    return flask.render_template("account_password.html", **context)


@coolmedia.app.route("/accounts/auth/", methods=["GET"])
def auth():
    """Verify that the username cookie is being stored."""
    if "username" not in flask.session:
        flask.abort(403)
    return "", 200
