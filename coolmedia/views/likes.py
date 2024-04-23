"""Insta485 Likes Method(s)."""
import flask
import coolmedia
from coolmedia.util import UsersPortal, LikesPortal
from coolmedia.util import get_target


@coolmedia.app.route("/likes/", methods=["POST"])
def like_unlike_post():
    """Likes or unlikes a post."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    operation = flask.request.form.get("operation")
    postid = flask.request.form.get("postid")
    curr_user = flask.session["username"]

    users_tb = UsersPortal()
    if not users_tb.verify_user(curr_user):
        return flask.redirect(flask.url_for("login"))

    likes_tb = LikesPortal()

    if not likes_tb.like_unlike(operation, postid, curr_user):
        flask.abort(409)
        # Error with liking or unliking

    return flask.redirect(get_target())
