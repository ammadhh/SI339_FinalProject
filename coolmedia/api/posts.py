"""REST API for posts."""
import pathlib
import flask
import coolmedia
from coolmedia.util import (
    PostsPortal,
    UsersPortal,
    CommentsPortal,
    LikesPortal,
    FollowingPortal,
)
from coolmedia.util import auth_user


@coolmedia.app.route("/api/v1/posts/", methods=["GET"])
def get_posts():
    """Return posts."""
    logname = auth_user()
    if logname == "":
        response = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(response), 403

    posts_tb = PostsPortal()
    following_tb = FollowingPortal()

    lte_num = flask.request.args.get("postid_lte", default=-1, type=int)
    num_post = flask.request.args.get("size", default=10, type=int)
    page = flask.request.args.get("page", default=0, type=int)

    if page < 0 or num_post <= 0:
        flask.abort(400)

    owners = following_tb.get_following_username(logname)
    owners.append(logname)

    results = posts_tb.get_post_restapi(owners, num_post, lte_num, page)

    for result in results:
        result["url"] = flask.request.path + f"{result['postid']}/"

    if lte_num == -1:
        lte_num = posts_tb.get_newest_post(owners)

    if len(results) >= num_post:
        next_url = (
            flask.request.path
            + f"?size={num_post}&page={page+1}&postid_lte={lte_num}"
        )
    else:
        next_url = ""

    url_path = flask.request.full_path
    if url_path[-1] == "?":
        url_path = url_path[:-1]

    context = {"next": next_url, "results": results, "url": url_path}
    return flask.jsonify(**context)


@coolmedia.app.route("/api/v1/posts/<int:postid_url_slug>/", methods=["GET"])
def get_one_post(postid_url_slug):
    """Return post on postid."""
    logname = auth_user()
    if logname == "":
        response = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(response), 403

    posts_tb = PostsPortal()
    comments_tb = CommentsPortal()
    likes_tb = LikesPortal()
    users_tb = UsersPortal()

    post_meta = posts_tb.get_post_with_id_restapi(postid_url_slug)
    comments = comments_tb.get_comments(postid_url_slug)

    for comment in comments:
        comment["lognameOwnsThis"] = comment["owner"] == logname
        comment["ownerShowUrl"] = (
            str(pathlib.Path("/users/") / comment["owner"]) + "/"
        )
        comment["url"] = (
            str(pathlib.Path("/api/v1/comments") / str(comment["commentid"]))
            + "/"
        )
        del comment["created"]

    if not post_meta:
        response = {"message": "Not Found", "status_code": 404}
        return flask.jsonify(response), 404

    context = {
        "comments": comments,
        "comments_url": str(
            pathlib.Path(f"/api/v1/comments/?postid={postid_url_slug}")
        ),
        "likes": likes_tb.get_like_restapi(postid_url_slug, logname),
        "ownerImgUrl": str(
            pathlib.Path("/uploads")
            / users_tb.get_user_img(post_meta["owner"])
        ),
        "ownerShowUrl": str(pathlib.Path("/users") / post_meta["owner"]) + "/",
        "postShowUrl": str(pathlib.Path("/posts") / str(postid_url_slug))
        + "/",
        "url": "/api/v1/posts/" + str(postid_url_slug) + "/",
    }
    context.update(post_meta)
    return flask.jsonify(**context)
