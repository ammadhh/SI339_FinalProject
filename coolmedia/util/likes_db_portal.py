"""Like db portal."""
import pathlib
import coolmedia


class LikesPortal:
    """Portal for likes DB."""

    # likeid
    # owner: FK users(username)
    # postid: FK posts(postid)
    # created
    def __init__(self):
        """Initialize function."""
        self.connection = coolmedia.model.get_db()

    def get_like_restapi(self, postid: int, logname: str):
        """Get like metadata."""
        logname_like = self.logname_likes_post(logname, postid)
        num_likes = self.get_post_likes(postid)
        url = (
            None
            if not logname_like
            else str(
                pathlib.Path("/api/v1/likes") / str(logname_like["likeid"])
            )
            + "/"
        )

        return {
            "lognameLikesThis": bool(logname_like),
            "numLikes": num_likes,
            "url": url,
        }

    def get_post_likes(self, postid: int) -> int:
        """Get number of likes for postid."""
        cur = self.connection.execute(
            "SELECT COUNT(*) "
            "FROM likes "
            "WHERE postid = ?", (postid,)
        )
        return cur.fetchone()["COUNT(*)"]

    def get_like_button(self, postid: int, owner: str) -> bool:
        """
        Get like status for owner on postid.

        True if owner has not liked the post.
        """
        cur = self.connection.execute(
            "SELECT * FROM likes "
            "WHERE postid = ? AND owner = ?",
            (postid, owner),
        )

        result = cur.fetchone()
        return not result

    def like_unlike(self, operation, postid, owner):
        """Like or Unlike Post and return False if there's some error."""
        cur = self.connection.execute(
            "SELECT * FROM likes "
            "WHERE postid = ? AND owner = ?",
            (postid, owner),
        )

        result = cur.fetchone()

        if operation == "like":
            if result is not None:
                return {
                    "likeid": result["likeid"],
                    "url": f"/api/v1/likes/{result['likeid']}",
                }
            self.connection.execute(
                "INSERT INTO likes (owner, postid)"
                "VALUES (?, ?)",
                (
                    owner,
                    postid,
                ),
            )
            return True
        if operation == "unlike":
            if result is None:
                return False
            self.connection.execute(
                "DELETE FROM likes"
                "WHERE postid = ? AND owner = ?",
                (
                    postid,
                    owner,
                ),
            )
            return True
        return True

    def like_post(self, postid, owner):
        """Perform a REST API Like of a post."""
        cur = self.connection.execute(
            "SELECT likeid FROM likes "
            "WHERE postid = ? AND owner = ?",
            (
                postid,
                owner,
            ),
        )

        result = cur.fetchone()

        if not result:
            self.connection.execute(
                "INSERT INTO likes (owner, postid)"
                "VALUES (?, ?)",
                (
                    owner,
                    postid,
                ),
            )

            cur_new = self.connection.execute(
                "SELECT likeid FROM likes "
                "WHERE postid = ? AND owner = ?",
                (
                    postid,
                    owner,
                ),
            )

            likeid = cur_new.fetchone()["likeid"]
            return [
                {"likeid": likeid, "url": f"/api/v1/likes/{likeid}/"},
                201,
            ]

        likeid = result["likeid"]
        return [
            {"likeid": likeid, "url": f"/api/v1/likes/{likeid}/"},
            200,
        ]

    def unlike_post(self, likeid, owner):
        """Unlikes post and returns http code."""
        cur = self.connection.execute(
            "SELECT owner FROM likes "
            "WHERE likeid = ?",
            (likeid,),
        )

        result = cur.fetchone()

        if not result:
            return 404
        if owner != result["owner"]:
            return 403

        self.connection.execute(
            """DELETE FROM likes
            WHERE likeid = ?""",
            (likeid,),
        )

        return 204

    def logname_likes_post(self, logname: str, postid: int) -> dict:
        """Return whether logname liked the post."""
        cur = self.connection.execute(
            "SELECT * from likes "
            "WHERE postid = ? AND owner = ?",
            (
                postid,
                logname,
            ),
        )

        result = cur.fetchone()

        return result
