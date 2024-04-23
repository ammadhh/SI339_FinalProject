import React, { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  const [created, setCreated] = useState("");
  const [likes, setLikes] = useState({
    lognameLikesThis: false,
    numLikes: 0,
    url: null,
  });
  const [likeReady, setLikeReady] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentsUrl, setCommentsUrl] = useState("");
  const [postid, setPostId] = useState(-1);
  const [showLike, setShowLike] = useState(true);

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setOwnerImgUrl(data.ownerImgUrl);
          setOwnerShowUrl(data.ownerShowUrl);
          setPostShowUrl(data.postShowUrl);
          setCreated(data.created);
          setLikes(data.likes);
          setLikeReady(true);
          setShowLike(!data.likes.lognameLikesThis);
          setComments(data.comments);
          setCommentsUrl(data.comments_url);
          setPostId(data.postid);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  const likeUnlike = useCallback(() => {
    if (likeReady) {
      setLikeReady(false);
      if (showLike) {
        fetch(`/api/v1/likes/?postid=${postid}`, {
          credentials: "same-origin",
          method: "POST",
        })
          .then((response) => {
            if (!response.ok) throw Error(response.statusText);
            return response.json();
          })
          .then((data) => {
            setLikes({
              lognameLikesThis: true,
              numLikes: likes.numLikes + 1,
              url: data.url,
            });
            setLikeReady(true);
          })
          .catch((error) => {
            console.log(error);
          });
      } else {
        fetch(likes.url, {
          credentials: "same-origin",
          method: "DELETE",
        })
          .then((response) => {
            setLikeReady(true);
            if (!response.ok) throw Error(response.statusText);
          })
          .catch((error) => {
            console.log(error);
          });
        setLikes({
          lognameLikesThis: false,
          numLikes: likes.numLikes - 1,
          url: null,
        });
      }
      setShowLike(!showLike);
    }
  }, [showLike, postid, likeReady, likes]);

  const handleLikeUnlike = useCallback(() => {
    likeUnlike();
  }, [likeUnlike]);

  const submitComment = useCallback(
    (e) => {
      e.preventDefault();

      const form = e.target;
      const formData = new FormData(form);
      const formJson = Object.fromEntries(formData.entries());
      fetch(commentsUrl, {
        method: form.method,
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(formJson),
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          setComments([...comments, data]);
          const inputField = document
            .getElementsByClassName("commentsForm")[0]
            .querySelector('input[name="text"]');
          if (inputField) {
            inputField.value = "";
          }
        })
        .catch((error) => {
          console.log(error);
        });
    },
    [commentsUrl, comments],
  );

  const deleteComment = useCallback(
    (e) => {
      e.preventDefault();
      const commentid = e.target.id;

      fetch(`/api/v1/comments/${commentid}/`, {
        method: "DELETE",
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          console.log(commentid);
          // console.log(JSON.stringify(comments));
          const newComments = comments.filter(
            (comment) => comment.commentid !== parseInt(commentid, 10),
          );
          setComments(newComments);
          // console.log(JSON.stringify(comments));
        })
        .catch((error) => {
          console.log(error);
        });
    },
    [comments],
  );

  const handleLikeIfUnliked = useCallback(() => {
    if (showLike) {
      likeUnlike();
    }
  }, [likeUnlike, showLike]);

  if (!url) {
    return <div>Loading</div>;
  }

  return (
    <Body
      ownerShowUrl={ownerShowUrl}
      ownerImgUrl={ownerImgUrl}
      owner={owner}
      comments={comments}
      postShowUrl={postShowUrl}
      created={created}
      imgUrl={imgUrl}
      likes={likes}
      postid={postid}
      showLike={showLike}
      likeUnlike={handleLikeUnlike}
      likeIfUnliked={handleLikeIfUnliked}
      submitComment={submitComment}
      deleteComment={deleteComment}
    />
  );
}

function Body({
  ownerShowUrl,
  ownerImgUrl,
  owner,
  comments,
  postShowUrl,
  created,
  imgUrl,
  likes,
  postid,
  showLike,
  likeUnlike,
  likeIfUnliked,
  submitComment,
  deleteComment,
}) {
  if (
    !ownerShowUrl ||
    !ownerImgUrl ||
    !owner ||
    !comments ||
    !postShowUrl ||
    !created ||
    !imgUrl ||
    postid === -1
  ) {
    return <div>Loading</div>;
  }

  return (
    <div className="post">
      <Header
        ownerShowUrl={ownerShowUrl}
        ownerImgUrl={ownerImgUrl}
        owner={owner}
        postShowUrl={postShowUrl}
        created={created}
      />
      <Img imgUrl={imgUrl} likeIfUnliked={likeIfUnliked} />
      <LikeSection likeMeta={likes} isLike={showLike} likeUnlike={likeUnlike} />
      <div className="comments">
        <CommentList comments={comments} deleteComment={deleteComment} />
      </div>
      <CommentForm submitComment={submitComment} postid={postid} />
    </div>
  );
}

function Header({ ownerShowUrl, ownerImgUrl, owner, postShowUrl, created }) {
  if (!ownerImgUrl || !ownerImgUrl || !owner || !postShowUrl || !created) {
    return <div>Loading</div>;
  }
  dayjs.extend(relativeTime);
  dayjs.extend(utc);
  const timestamp = dayjs(created).utc().local().fromNow();

  return (
    <div>
      <a href={ownerShowUrl}>
        <img src={ownerImgUrl} alt={owner} className="profile" />
      </a>
      <a href={ownerShowUrl}>{owner}</a>
      <a href={postShowUrl}> {timestamp} </a>
    </div>
  );
}

function Img({ imgUrl, likeIfUnliked }) {
  if (!imgUrl) {
    return <div>Loading</div>;
  }

  return (
    <img
      src={imgUrl}
      alt="post_image"
      className="upload"
      onDoubleClick={likeIfUnliked}
    />
  );
}

function LikeSection({ likeMeta, isLike, likeUnlike }) {
  if (!likeMeta) {
    return <div>Loading</div>;
  }
  const likeStr =
    likeMeta.numLikes === 1 ? "1 like" : `${likeMeta.numLikes} likes`;
  return (
    <div>
      <span>{likeStr}</span>
      <button
        type="button"
        data-testid="like-unlike-button"
        onClick={likeUnlike}
      >
        {isLike ? "like" : "unlike"}
      </button>
    </div>
  );
}

function CommentForm({ submitComment, postid }) {
  return (
    <form
      method="post"
      encType="multipart/form-data"
      data-testid="comment-form"
      onSubmit={submitComment}
      className="commentsForm"
    >
      <input type="hidden" name="operation" value="create" />
      <input type="hidden" name="postid" value={postid} />
      <input type="text" name="text" required />
      <input
        type="submit"
        style={{ display: "none" }}
        name="comment"
        value="comment"
      />
    </form>
  );
}

function CommentList({ comments, deleteComment }) {
  if (!comments) {
    return <div>Loading</div>;
  }
  return (
    <ul>
      {comments.map((comment) => (
        <Comment
          key={comment.commentid}
          comment={comment}
          deleteComment={deleteComment}
        />
      ))}
    </ul>
  );
}

function Comment({ comment, deleteComment }) {
  if (!comment) {
    return <div>Loading</div>;
  }
  return (
    <li key={comment.commentid}>
      <a href={comment.ownerShowUrl}> {comment.owner} </a>
      <span data-testid="comment-text"> {comment.text} </span>
      {comment.lognameOwnsThis && (
        <span>
          <button
            type="button"
            data-testid="delete-comment-button"
            id={comment.commentid}
            onClick={deleteComment}
          >
            Delete comment
          </button>
        </span>
      )}
    </li>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

Body.propTypes = {
  ownerShowUrl: PropTypes.string.isRequired,
  ownerImgUrl: PropTypes.string.isRequired,
  owner: PropTypes.string.isRequired,
  comments: PropTypes.arrayOf(Comment).isRequired,
  postShowUrl: PropTypes.string.isRequired,
  created: PropTypes.string.isRequired,
  imgUrl: PropTypes.string.isRequired,
  likes: PropTypes.shape({
    lognameLikesThis: PropTypes.bool.isRequired,
    numLikes: PropTypes.number.isRequired,
  }).isRequired,
  showLike: PropTypes.bool.isRequired,
  postid: PropTypes.number.isRequired,
  likeUnlike: PropTypes.func.isRequired,
  likeIfUnliked: PropTypes.func.isRequired,
  submitComment: PropTypes.func.isRequired,
  deleteComment: PropTypes.func.isRequired,
};

Comment.propTypes = {
  comment: PropTypes.shape({
    commentid: PropTypes.number.isRequired,
    ownerShowUrl: PropTypes.string.isRequired,
    owner: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    lognameOwnsThis: PropTypes.bool.isRequired,
  }).isRequired,
  deleteComment: PropTypes.func.isRequired,
};

CommentList.propTypes = {
  comments: PropTypes.arrayOf(Comment).isRequired,
  deleteComment: PropTypes.func.isRequired,
};

CommentForm.propTypes = {
  submitComment: PropTypes.func.isRequired,
  postid: PropTypes.number.isRequired,
};

Header.propTypes = {
  ownerShowUrl: PropTypes.string.isRequired,
  ownerImgUrl: PropTypes.string.isRequired,
  owner: PropTypes.string.isRequired,
  postShowUrl: PropTypes.string.isRequired,
  created: PropTypes.string.isRequired,
};

Img.propTypes = {
  imgUrl: PropTypes.string.isRequired,
  likeIfUnliked: PropTypes.func.isRequired,
};

LikeSection.propTypes = {
  likeMeta: PropTypes.shape({
    lognameLikesThis: PropTypes.bool.isRequired,
    numLikes: PropTypes.number.isRequired,
  }).isRequired,
  isLike: PropTypes.bool.isRequired,
  likeUnlike: PropTypes.func.isRequired,
};

CommentForm.propTypes = {
  submitComment: PropTypes.func.isRequired,
  postid: PropTypes.number.isRequired,
};
