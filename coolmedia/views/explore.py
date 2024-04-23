"""
Insta485 explore view.

URLs include:
/explore/
"""
import pathlib
import flask
import coolmedia
from coolmedia.util import FollowingPortal, UsersPortal


@coolmedia.app.route("/explore/")
def explore():
    """Routes to the Explore Page."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    users_tb = UsersPortal()
    following_tb = FollowingPortal()

    logname = flask.session["username"]
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    username_list = users_tb.all_username(logname)
    not_following = []
    for username in username_list:
        if not following_tb.get_specific_following(logname, username):
            not_following.append(
                {
                    "user_img_url": pathlib.Path("/uploads/")
                    / users_tb.get_user_img(username),
                    "username": username,
                }
            )

    context = {"logname": logname, "not_following": not_following}

    return flask.render_template("explore.html", **context)
