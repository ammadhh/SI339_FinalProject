"""Comment db portal."""
import coolmedia
from coolmedia.util.helper import get_time_int


class CommentsPortal:
    """Portal for comments db."""

    # commentid
    # owner: FK users(username)
    # postid: FK posts(postid)
    # text
    # created
    def __init__(self):
        """Initialize function."""
        self.connection = coolmedia.model.get_db()

    def get_comments(self, postid: int) -> list:
        """Get sorted comments for postid."""
        cur = self.connection.execute(
            "SELECT owner, text, created, commentid "
            "FROM comments "
            "WHERE postid = ?",
            (postid,),
        )

        comment_list = cur.fetchall()

        def custom_sort_key(item):
            return (get_time_int(item["created"]), item["commentid"])

        if comment_list:
            comment_list = sorted(comment_list, key=custom_sort_key)
        return comment_list

    def create_comment(self, postid, text, owner) -> bool:
        """
        Attempt to create a comment.

        Return False if the text is empty.
        """
        if len(text) == 0:
            return False

        self.connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?)",
            (owner, postid, text),
        )

        return True

    def post_comment_api(self, text, postid, owner):
        """
        Attempt to create a comment.

        Return False if the text is empty.
        """
        if len(text) == 0:
            return False

        self.connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?)",
            (owner, postid, text),
        )
        cur = self.connection.execute("SELECT last_insert_rowid()")
        last_comment_id = cur.fetchone()

        return last_comment_id

    def delete_comment(self, commentid, owner) -> bool:
        """
        Attempt to delete a comment and will return False.

        if owner passed in isn't owner of comment.
        """
        cur = self.connection.execute(
            "SELECT owner "
            "FROM comments "
            "WHERE commentid = ?",
            (commentid,),
        )

        comment_owner = cur.fetchone()["owner"]

        if comment_owner != owner:
            return False

        self.connection.execute(
            "DELETE FROM comments "
            "WHERE commentid = ?",
            (commentid,),
        )

        return True

    def api_delete_comment(self, commentid, owner) -> int:
        """Delete comment rest api."""
        cur = self.connection.execute(
            "SELECT owner "
            "FROM comments "
            "WHERE commentid = ? ",
            (commentid,),
        )

        comment_owner = cur.fetchone()
        if not comment_owner:
            return 404
        comment_owner = comment_owner["owner"]

        if comment_owner != owner:
            return 403

        self.connection.execute(
            "DELETE FROM comments "
            "WHERE commentid = ?",
            (commentid,),
        )

        return 204
