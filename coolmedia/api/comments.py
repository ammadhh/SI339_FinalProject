"""Comment api."""
import flask
import coolmedia
from coolmedia.util import PostsPortal, CommentsPortal
from coolmedia.util import auth_user


@coolmedia.app.route(
    "/api/v1/comments/",
    methods=[
        "POST",
    ],
)
def add_comment():
    """Comments on a post and returns json object."""
    postid_url_slug = flask.request.args.get("postid")
    logname = auth_user()
    if logname == "":
        return flask.jsonify(
            {"message": "Forbidden", "status_code": 403}
            ), 403

    comment_tb = CommentsPortal()
    posts_tb = PostsPortal()

    if not posts_tb.get_post_with_id_restapi(postid_url_slug):
        response = {"message": "Not Found", "status_code": 404}
        return flask.jsonify(response), 404

    fullitems = {
        "owner": logname,
        "lognameOwnsThis": True,
        "ownerShowUrl": f"/users/{logname}/",
    }
    if flask.request.json and "text" in flask.request.json:
        text = flask.request.json["text"]
        # Now you can use the 'text' variable in your code
        fullitems["text"] = text
        comment_id = comment_tb.post_comment_api(
            text, postid_url_slug, logname
        )["last_insert_rowid()"]
        fullitems["commentid"] = comment_id
        fullitems["url"] = flask.request.path + f"{comment_id}/"

    return flask.jsonify(**fullitems), 201


@coolmedia.app.route(
    "/api/v1/comments/<int:commentid_url_slug>/",
    methods=[
        "DELETE",
    ],
)
def delete_comment(commentid_url_slug):
    """Delete the comment based on the comment id."""
    logname = auth_user()
    if logname == "":
        response = {"message": "Forbidden", "status_code": 403}
        return flask.jsonify(response), 403

    comments_tb = CommentsPortal()
    http_code = comments_tb.api_delete_comment(commentid_url_slug, logname)
    if http_code != 204:
        response = {
            "message": "Not Found" if http_code == 404 else "Forbidden",
            "status_code": http_code,
        }
        return flask.jsonify(response), http_code

    return ("", http_code)
