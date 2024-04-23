"""sqlite DB portal."""

import coolmedia
from coolmedia.views.helper import get_time, get_time_int, password_hash


class DbPortal:
    """Parent class of all DB portals."""

    def __init__(self):
        """Connect to database."""
        self.connection = coolmedia.model.get_db()


class UsersPortal(DbPortal):
    """Portal to users DB."""

    # username
    # fullname
    # email
    # filename
    # password
    # salt
    # created
    def all_username(self, logname: str) -> list:
        """Return all username except logname."""
        cur = self.connection.execute(
            "SELECT username "
            "FROM users "
            "WHERE username != ?",
            (logname, )
        )
        usernames = cur.fetchall()
        return [u["username"] for u in usernames]

    def create(self, filename: str, username: str,
               fullname: str, email: str, password: str):
        """Store newly created account."""
        hashed_password = password_hash(password)
        self.connection.execute(
            "INSERT INTO users "
            "(username, fullname, email, filename, password) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, fullname, email, filename, hashed_password)
            )

    def update(self, username: str, fullname: str,
               email: str, filename=None):
        """Update user profile."""
        self.connection.execute(
            "UPDATE users "
            "SET fullname = ?, email = ? "
            "WHERE username = ? ",
            (fullname, email, username)
        )

        if filename:
            self.connection.execute(
                "UPDATE users "
                "SET filename = ? "
                "WHERE username = ? ",
                (filename, username)
            )

    def update_password(self, username: str, new_password: str):
        """Update username password."""
        self.connection.execute(
            "UPDATE users "
            "SET password = ? "
            "WHERE username = ? ",
            (new_password, username)
        )

    def delete(self, username: str):
        """Delete username account."""
        self.connection.execute(
            "DELETE FROM users "
            "WHERE username = ?",
            (username, )
        )

    def get_user_img(self, username: str) -> str:
        """Get img url for username."""
        cur = self.connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (username, )
        )

        return cur.fetchone()["filename"]

    def get_user_fullname(self, username: str) -> str:
        """Get fullname of username."""
        cur = self.connection.execute(
            "SELECT fullname "
            "FROM users "
            "WHERE username = ?",
            (username, )
        )

        return cur.fetchone()["fullname"]

    def get_user_email(self, username: str) -> str:
        """Get email of username."""
        cur = self.connection.execute(
            "SELECT email "
            "FROM users "
            "WHERE username = ?",
            (username, )
        )

        return cur.fetchone()["email"]

    def verify_user(self, username: str) -> bool:
        """Verify that the user exists in database."""
        cur = self.connection.execute(
            "SELECT fullname "
            "FROM users "
            "WHERE username = ?",
            (username, )
        )

        return cur.fetchone() is not None

    def verify_password(self, username: str, password: str) -> bool:
        """
        Verify whether the password is correct.

        Return False if there is no username or password does not match.
        """
        cur = self.connection.execute(
            "SELECT password "
            "FROM users "
            "WHERE username = ?",
            (username, )
        )

        result = cur.fetchone()
        if not result:
            return False

        stored_password = result["password"]
        salt = stored_password.split("$")[1]
        hashed_password = password_hash(password, salt)

        if hashed_password != stored_password:
            return False
        return True


class PostsPortal(DbPortal):
    """Portal for posts DB."""

    # postid
    # filename
    # owner: FK users(username)
    # created
    def get_post_list(self, owner: str, count_only=False) -> list:
        """Get all the posts data of the owner."""
        cur = self.connection.execute(
            "SELECT postid, created, owner, filename "
            "FROM posts "
            "WHERE owner = ?",
            (owner, )
        )

        posts = cur.fetchall()

        if count_only:
            return len(posts)

        return posts

    def get_post(self, postid: int):
        """Get all post info."""
        cur = self.connection.execute(
            "SELECT filename, owner, created, postid "
            "FROM posts "
            "WHERE postid = ?",
            (postid, )
        )

        post = cur.fetchone()
        post["img_url"] = "/uploads/" + post.pop("filename")
        post["timestamp"] = get_time(post.pop("created"))

        return post

    def get_filename(self, postid):
        """Get the filename for a specific post."""
        cur = self.connection.execute(
            """SELECT filename FROM posts
                WHERE postid = ?""",
            (postid, )
        )

        return cur.fetchone()["filename"]

    def create_post(self, filename, owner):
        """Create a new post."""
        self.connection.execute(
            """INSERT INTO posts(filename, owner)
                VALUES (?, ?)""",
            (filename, owner)
        )

    def delete_post(self, postid, owner) -> bool:
        """
        Delete a post.

        Return false if owner is not attached to postid.
        """
        cur = self.connection.execute(
            """SELECT owner FROM posts
                WHERE postid = ?""",
            (postid,)
        )

        post_owner = cur.fetchone()["owner"]

        if post_owner != owner:
            return False

        self.connection.execute(
            """DELETE from posts
                WHERE postid = ?""",
            (postid, )
        )

        return True


class FollowingPortal(DbPortal):
    """Portal for following DB."""

    # username1: FK users(username)
    # username2: FK users(username)
    #            username1 follows username2
    # created
    # count_only parameter will only
    # return the length of the list of followers or following
    def get_following_username(self, username: str, count_only=False):
        """Get all the people that username is following."""
        cur = self.connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (username, )
        )

        follower_list = cur.fetchall()
        if count_only:
            return len(follower_list)
        return [entry['username2'] for entry in follower_list]

    def get_followers_username(self, username: str, count_only=False):
        """Get all the usernames that are followers of username."""
        cur = self.connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username2 = ?",
            (username, )
        )

        following_list = cur.fetchall()
        if count_only:
            return len(following_list)
        return [entry['username1'] for entry in following_list]

    def get_specific_following(self, logname: str, curr_user: str) -> bool:
        """Return whether logname follows curr_user."""
        curr = self.connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, curr_user, )
        )

        following = curr.fetchone()
        return following is not None

    def follow_user(self, logname, username) -> bool:
        """Attempt to follow a user and returns false if already following."""
        cur = self.connection.execute(
            """SELECT * FROM following
                WHERE username1 = ? AND username2 = ?""",
            (logname, username)
        )

        if cur.fetchone():
            return False

        self.connection.execute(
                """INSERT INTO following(username1, username2)
                   VALUES (?, ?)""",
                (logname, username)
        )

        return True

    def unfollow_user(self, logname, username) -> bool:
        """
        Attempt to unfollow a user.

        Return false if not following user.
        """
        cur = self.connection.execute(
            """SELECT * FROM following
                WHERE username1 = ? AND username2 = ?""",
            (logname, username)
        )

        if not cur.fetchone():
            return False

        self.connection.execute(
            """DELETE FROM following
                WHERE username1 = ? AND username2 = ?""",
            (logname, username)
        )

        return True


class CommentsPortal(DbPortal):
    """Portal for comments db."""

    # commentid
    # owner: FK users(username)
    # postid: FK posts(postid)
    # text
    # created
    def get_comments(self, postid: int) -> list:
        """Get sorted comments for postid."""
        cur = self.connection.execute(
            "SELECT owner, text, created, commentid "
            "FROM comments "
            "WHERE postid = ?",
            (postid, )
        )

        comment_list = cur.fetchall()

        def custom_sort_key(item):
            return get_time_int(item["created"])

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
            """INSERT INTO comments (owner, postid, text)
                VALUES (?, ?, ?)""",
            (owner, postid, text)
        )

        return True

    def delete_comment(self, commentid, owner) -> bool:
        """
        Attempt to delete a comment and will return False.

        if owner passed in isn't owner of comment.
        """
        cur = self.connection.execute(
            """SELECT owner
                FROM comments
                WHERE commentid = ?""",
            (commentid,)
        )

        comment_owner = cur.fetchone()["owner"]

        if comment_owner != owner:
            return False

        self.connection.execute(
            """DELETE FROM comments
                WHERE commentid = ?""",
            (commentid,)
        )

        return True


class LikesPortal(DbPortal):
    """Portal for likes DB."""

    # likeid
    # owner: FK users(username)
    # postid: FK posts(postid)
    # created
    def get_post_likes(self, postid: int) -> int:
        """Get number of likes for postid."""
        cur = self.connection.execute(
            "SELECT COUNT(*) "
            "FROM likes "
            "WHERE postid = ?",
            (postid,)
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
            (postid, owner)
        )

        result = cur.fetchone()
        return not result

    def like_unlike(self, operation, postid, owner) -> bool:
        """Like or Unlike Post and return False if there's some error."""
        cur = self.connection.execute(
            "SELECT * FROM likes "
            "WHERE postid = ? AND owner = ?",
            (postid, owner)
        )

        result = cur.fetchone()

        if operation == "like":
            if result is not None:
                return False
            self.connection.execute(
                "INSERT INTO likes (owner, postid)"
                "VALUES (?, ?)",
                (owner, postid, )
            )
            return True
        if operation == "unlike":
            if result is None:
                return False
            self.connection.execute(
                """DELETE FROM likes
                   WHERE postid = ? AND owner = ?""",
                (postid, owner, )
            )
            return True
        return True
