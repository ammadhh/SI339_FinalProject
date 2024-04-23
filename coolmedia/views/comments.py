"""Implement Commenting Functionality."""
import flask
import coolmedia
from coolmedia.util import UsersPortal, CommentsPortal
from coolmedia.util import get_target


@coolmedia.app.route("/comments/", methods=["POST"])
def create_delete_comment():
    """Create or delete a comment."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    operation = flask.request.form.get("operation")
    postid = flask.request.form.get("postid")
    commentid = flask.request.form.get("commentid")
    text = flask.request.form.get("text")
    curr_user = flask.session["username"]

    users_tb = UsersPortal()
    if not users_tb.verify_user(curr_user):
        return flask.redirect(flask.url_for("login"))

    comments_tb = CommentsPortal()

    if operation == "create":
        if not comments_tb.create_comment(postid, text, curr_user):
            flask.abort(400)

    elif operation == "delete":
        if not comments_tb.delete_comment(commentid, curr_user):
            flask.abort(403)

    return flask.redirect(get_target())
