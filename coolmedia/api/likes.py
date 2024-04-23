"""Like api."""
import flask
import coolmedia
from coolmedia.util import PostsPortal, LikesPortal
from coolmedia.util import auth_user


@coolmedia.app.route(
    "/api/v1/likes/",
    methods=[
        "POST",
    ],
)
def like_post():
    """Likes a post and returns like object."""
    postid_url_slug = flask.request.args.get("postid")
    logname = auth_user()
    if logname == "":
        response = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**response), 403

    likes_tb = LikesPortal()
    posts_tb = PostsPortal()

    post = posts_tb.get_post(postid_url_slug)
    if not post:  # If post is out of range, abort with 404 error
        response = {"message": "Not Found", "status_code": 404}
        return flask.jsonify(**response), 404

    likes_obj = likes_tb.like_post(postid_url_slug, logname)

    context = likes_obj[0]

    return flask.jsonify(**context), likes_obj[1]


@coolmedia.app.route(
    "/api/v1/likes/<int:likeid_url_slug>/",
    methods=[
        "DELETE",
    ],
)
def unlike_post(likeid_url_slug):
    """Unlikes a post and aborts if there's an error."""
    logname = auth_user()
    if logname == "":
        response = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(**response), 403

    likes_tb = LikesPortal()

    http_code = likes_tb.unlike_post(likeid_url_slug, logname)

    if http_code != 204:
        flask.abort(http_code)

    return flask.jsonify(**{}), http_code
