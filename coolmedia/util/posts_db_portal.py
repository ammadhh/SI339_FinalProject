"""Posts db portal."""
import coolmedia
from coolmedia.util.helper import get_time


class PostsPortal:
    """Portal for posts DB."""

    # postid
    # filename
    # owner: FK users(username)
    # created
    def __init__(self):
        """Initialize function."""
        self.connection = coolmedia.model.get_db()

    def get_post_list(
        self, owner: str, count_only: bool = False
    ):
        """Get all the posts data of the owner."""
        cur = self.connection.execute(
            "SELECT postid, created, owner, filename "
            "FROM posts "
            "WHERE owner = ?"
            "ORDER BY created DESC, postid DESC ",
            (owner,),
        )

        posts = cur.fetchall()

        if count_only:
            return len(posts)

        return posts

    def get_post_restapi(
        self, owner_list: list, size: int = 10, lte: int = -1, page: int = 0
    ):
        """Get all the posts in owner list."""
        placeholders = ", ".join(["?"] * len(owner_list))

        if lte == -1:
            query_param = tuple(owner_list) + (
                size,
                size * page,
            )
            cur = self.connection.execute(
                "SELECT postid "
                "FROM posts "
                f"WHERE owner IN ({placeholders}) "
                "ORDER BY created DESC, postid DESC "
                "LIMIT ? "
                "OFFSET ?",
                query_param,
            )
        else:
            query_param = tuple(owner_list) + (lte, size, size * page)
            cur = self.connection.execute(
                "SELECT postid "
                "FROM posts "
                f"WHERE owner IN ({placeholders}) AND postid <= ? "
                "ORDER BY created DESC, postid DESC "
                "LIMIT ? "
                "OFFSET ? ",
                query_param,
            )

        posts = cur.fetchall()
        return posts

    def get_post_with_id_restapi(self, postid: int):
        """Get all post info."""
        cur = self.connection.execute(
            "SELECT created, owner, postid, filename "
            "FROM posts "
            "WHERE postid = ?",
            (postid,),
        )

        post = cur.fetchone()
        if not post:
            return None
        post["imgUrl"] = "/uploads/" + post.pop("filename")
        return post

    def get_newest_post(self, owner_list: list) -> int:
        """Get the newest post."""
        placeholders = ", ".join(["?"] * len(owner_list))

        query_param = tuple(owner_list)
        cur = self.connection.execute(
            "SELECT MAX(postid) "
            "FROM posts "
            f"WHERE owner IN ({placeholders}) ",
            query_param,
        )
        return cur.fetchone()["MAX(postid)"]

    def get_post(self, postid: int):
        """Get all post info."""
        cur = self.connection.execute(
            "SELECT filename, owner, created, postid "
            "FROM posts "
            "WHERE postid = ?",
            (postid,),
        )

        post = cur.fetchone()
        if not post:
            return post
        post["img_url"] = "/uploads/" + post.pop("filename")
        post["timestamp"] = get_time(post["created"])

        return post

    def get_filename(self, postid):
        """Get the filename for a specific post."""
        cur = self.connection.execute(
            "SELECT filename FROM posts "
            "WHERE postid = ?",
            (postid,),
        )

        return cur.fetchone()["filename"]

    def create_post(self, filename, owner):
        """Create a new post."""
        self.connection.execute(
            "INSERT INTO posts(filename, owner) "
            "VALUES (?, ?)",
            (filename, owner),
        )

    def delete_post(self, postid, owner) -> bool:
        """
        Delete a post.

        Return false if owner is not attached to postid.
        """
        cur = self.connection.execute(
            "SELECT owner FROM posts "
            "WHERE postid = ?",
            (postid,),
        )

        post_owner = cur.fetchone()["owner"]

        if post_owner != owner:
            return False

        self.connection.execute(
            "DELETE from posts "
            "WHERE postid = ?",
            (postid,),
        )

        return True
