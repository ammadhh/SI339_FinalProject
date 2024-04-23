"""Base REST API file."""
import flask
import coolmedia


@coolmedia.app.route("/api/v1/")
def return_services():
    """Return API resource URLs."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/",
    }

    return flask.jsonify(**context)
