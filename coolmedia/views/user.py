"""
Insta485 User view.

URLs include:
/users/<get_user_slug>/
/users/<get_user_slug>/followers/
/users/<get_user_slug>/following/
"""
import pathlib
import flask
import coolmedia
from coolmedia.util import FollowingPortal, PostsPortal, UsersPortal
from coolmedia.util import get_time_int


@coolmedia.app.route("/users/<get_user_slug>/")
def get_user(get_user_slug):
    """Get the user page of user specified by slug."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    users_tb = UsersPortal()

    if not users_tb.verify_user(get_user_slug):
        flask.abort(404)

    logname = flask.session["username"]
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    following_tb = FollowingPortal()

    logname_following_user = following_tb.get_specific_following(
        logname, get_user_slug
    )

    posts_tb = PostsPortal()

    posts_list = posts_tb.get_post_list(get_user_slug)
    posts_count = len(posts_list)

    def custom_sort_key(item):
        return (-get_time_int(item["created"]), item["postid"])

    posts_list = sorted(posts_list, key=custom_sort_key)

    for post in posts_list:
        post["img_url"] = pathlib.Path("/uploads/") / post.pop("filename")

    followers = following_tb.get_followers_username(
        get_user_slug, count_only=True
    )
    following = following_tb.get_following_username(
        get_user_slug, count_only=True
    )

    full_name = users_tb.get_user_fullname(get_user_slug)

    context = {
        "logname": logname,
        "username": get_user_slug,
        "logname_follows_username": logname_following_user,
        "total_posts": posts_count,
        "followers": followers,
        "following": following,
        "fullname": full_name,
        "posts": posts_list,
    }

    return flask.render_template("user.html", **context)


@coolmedia.app.route("/users/<get_user_slug>/followers/")
def get_user_followers(get_user_slug):
    """Get the followers of the current user."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    following_tb = FollowingPortal()
    users_tb = UsersPortal()

    if not users_tb.verify_user(get_user_slug):
        flask.abort(404)

    logname = flask.session["username"]
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    followers_names = following_tb.get_followers_username(get_user_slug)

    followers = []

    for follower in followers_names:
        followers.append(
            {
                "user_img_url": pathlib.Path("/uploads/")
                / users_tb.get_user_img(follower),
                "username": follower,
                "logname_follows_username":
                    following_tb.get_specific_following(
                        logname, follower
                    ),
            }
        )

    context = {
        "logname": logname,
        "username": get_user_slug,
        "followers": followers,
    }

    return flask.render_template("followers.html", **context)


@coolmedia.app.route("/users/<get_user_slug>/following/")
def get_user_following(get_user_slug):
    """Get all the users that the current user is following."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    following_tb = FollowingPortal()
    users_tb = UsersPortal()

    if not users_tb.verify_user(get_user_slug):
        flask.abort(404)

    logname = flask.session["username"]
    if not users_tb.verify_user(logname):
        return flask.redirect(flask.url_for("login"))

    following_names = following_tb.get_following_username(get_user_slug)

    following = []

    for follower in following_names:
        following.append(
            {
                "user_img_url": pathlib.Path("/uploads/")
                / users_tb.get_user_img(follower),
                "username": follower,
                "logname_follows_username":
                    following_tb.get_specific_following(
                        logname, follower
                    ),
            }
        )

    context = {
        "logname": logname,
        "username": get_user_slug,
        "following": following,
    }

    return flask.render_template("following.html", **context)
