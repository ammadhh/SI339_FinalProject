"""Insta485 Following and Unfollowing User Functionality."""
import flask
import coolmedia
from coolmedia.util import FollowingPortal, UsersPortal
from coolmedia.util import get_target


@coolmedia.app.route("/following/", methods=["POST"])
def follow_unfollow():
    """Follow or unfollow a user."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    operation = flask.request.form.get("operation")
    username = flask.request.form.get("username")
    logname = flask.session["username"]

    users_tb = UsersPortal()
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    following_tb = FollowingPortal()

    if operation == "follow":
        if not following_tb.follow_user(logname, username):
            flask.abort(409)
            # Abort if already following user

    elif operation == "unfollow":
        if not following_tb.unfollow_user(logname, username):
            flask.abort(409)
            # Abort if we aren't already following user

    return flask.redirect(get_target())
