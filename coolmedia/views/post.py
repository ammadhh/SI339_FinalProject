"""
Insta485 post view.

URLs include:
/posts/<postid_url_slug>/
"""

import os
import pathlib
import flask
import coolmedia
from coolmedia.util import PostsPortal, UsersPortal, LikesPortal, CommentsPortal
from coolmedia.util import get_target, store_file, check_filename


@coolmedia.app.route("/posts/<postid_url_slug>/")
def show_post(postid_url_slug):
    """Show post specified by slug."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    postid = int(postid_url_slug)

    post_tb = PostsPortal()
    users_tb = UsersPortal()
    comment_tb = CommentsPortal()
    likes_tb = LikesPortal()

    logname = flask.session["username"]

    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    post = post_tb.get_post(postid)
    uploads_folder = pathlib.Path("/uploads/")
    post["owner_img_url"] = uploads_folder / users_tb.get_user_img(
        post["owner"]
    )
    post["show_like"] = likes_tb.get_like_button(post["postid"], logname)
    post["show_delete"] = post["owner"] == logname
    comments = comment_tb.get_comments(postid)
    for comment in comments:
        comment["show_delete"] = False
        if logname == comment["owner"]:
            comment["show_delete"] = True

    context = {
        "logname": logname,
        "post": post,
        "comments": comments,
        "likes": likes_tb.get_post_likes(postid),
    }

    return flask.render_template("post.html", **context)


@coolmedia.app.route("/posts/", methods=["POST"])
def create_delete_post():
    """Create or Delete a post."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    posts_tb = PostsPortal()

    operation = flask.request.form.get("operation")
    logname = flask.session["username"]

    users_tb = UsersPortal()
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    if operation == "create":
        if "file" not in flask.request.files:
            flask.abort(400)
        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.name
        check_filename(filename)

        # Compute base name (filename without directory).
        # We use a UUID to avoid clashes with existing files,
        # and ensure that the name is compatible with the
        # filesystem. For best practice,
        #  we ensure uniform file extensions (e.g. lowercase).

        uuid_basename = store_file(filename, fileobj)
        posts_tb.create_post(uuid_basename, logname)
    elif operation == "delete":
        postid = flask.request.form.get("postid")

        filename = posts_tb.get_filename(postid)

        if not posts_tb.delete_post(postid, logname):
            flask.abort(403)

        file_path = (
            pathlib.Path(coolmedia.app.config["UPLOAD_FOLDER"]) / filename
        )

        os.remove(file_path)

    return flask.redirect(get_target())
