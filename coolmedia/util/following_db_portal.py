"""Following db portal."""
import coolmedia


class FollowingPortal:
    """Portal for following DB."""

    # username1: FK users(username)
    # username2: FK users(username)
    #            username1 follows username2
    # created
    # count_only parameter will only
    # return the length of the list of followers or following
    def __init__(self):
        """Initialize function."""
        self.connection = coolmedia.model.get_db()

    def get_following_username(self, username: str, count_only=False):
        """Get all the people that username is following."""
        cur = self.connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ?",
            (username,),
        )

        follower_list = cur.fetchall()
        if count_only:
            return len(follower_list)
        return [entry["username2"] for entry in follower_list]

    def get_followers_username(self, username: str, count_only=False):
        """Get all the usernames that are followers of username."""
        cur = self.connection.execute(
            "SELECT username1 "
            "FROM following "
            "WHERE username2 = ?",
            (username,),
        )

        following_list = cur.fetchall()
        if count_only:
            return len(following_list)
        return [entry["username1"] for entry in following_list]

    def get_specific_following(self, logname: str, curr_user: str) -> bool:
        """Return whether logname follows curr_user."""
        curr = self.connection.execute(
            "SELECT username2 "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (
                logname,
                curr_user,
            ),
        )

        following = curr.fetchone()
        return following is not None

    def follow_user(self, logname, username) -> bool:
        """Attempt to follow a user and returns false if already following."""
        cur = self.connection.execute(
            "SELECT * FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, username),
        )

        if cur.fetchone():
            return False

        self.connection.execute(
            "INSERT INTO following(username1, username2) "
            "VALUES (?, ?)",
            (logname, username),
        )

        return True

    def unfollow_user(self, logname, username) -> bool:
        """
        Attempt to unfollow a user.

        Return false if not following user.
        """
        cur = self.connection.execute(
            "SELECT * FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, username),
        )

        if not cur.fetchone():
            return False

        self.connection.execute(
            "DELETE FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (logname, username),
        )

        return True
