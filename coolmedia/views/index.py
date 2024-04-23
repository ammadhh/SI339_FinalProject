"""
Insta485 index (main) view.

URLs include:
/
"""
import pathlib
import os
import flask
import coolmedia
from coolmedia.util import (
    FollowingPortal,
    PostsPortal,
    UsersPortal,
    LikesPortal,
    CommentsPortal,
)
from coolmedia.util import get_time, get_time_int


@coolmedia.app.route("/")
def show_index():
    """Display / route."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    # Connect to database
    following_tb = FollowingPortal()
    posts_tb = PostsPortal()
    users_tb = UsersPortal()
    likes_tb = LikesPortal()
    comments_tb = CommentsPortal()

    logname = flask.session["username"]
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    following_list = following_tb.get_following_username(logname)

    post_dict_list = posts_tb.get_post_list(logname)
    for user in following_list:
        post_dict_list.extend(posts_tb.get_post_list(user))

    def custom_sort_key(item):
        return (-get_time_int(item["created"]), item["postid"])

    sorted_post_dict_list = sorted(post_dict_list, key=custom_sort_key)

    for post in sorted_post_dict_list:
        post["img_url"] = pathlib.Path("/uploads/") / post.pop("filename")
        post["timestamp"] = get_time(post.pop("created"))
        post["owner_img_url"] = pathlib.Path(
            "/uploads/"
        ) / users_tb.get_user_img(post["owner"])
        post["likes"] = likes_tb.get_post_likes(post["postid"])
        post["comments"] = comments_tb.get_comments(post["postid"])
        post["show_like"] = likes_tb.get_like_button(post["postid"], logname)

    context = {
        "logname": logname,
        "posts": sorted_post_dict_list,
    }
    return flask.render_template("index.html", **context)


@coolmedia.app.route("/static/<path:path>")
def serve_static_file(path):
    """Fetch static file."""
    return flask.send_from_directory("static", path)


@coolmedia.app.route("/uploads/<path:path>")
def serve_path(path):
    """Serve uploads file."""
    if "username" not in flask.session:
        return flask.abort(403)

    full_path = coolmedia.app.config["UPLOAD_FOLDER"] / path
    if not os.path.exists(full_path):
        return flask.abort(404)

    return flask.send_from_directory(
        coolmedia.app.config["UPLOAD_FOLDER"], path
    )
