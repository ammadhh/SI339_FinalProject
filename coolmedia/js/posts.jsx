import React, { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

export default function Posts({ url }) {
  const [posts, setPosts] = useState([]);
  const [next, setNext] = useState("");

  useEffect(() => {
    let ignoreStaleRequest = false;
    console.log("Trying fetch");
    console.log(url);
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (!ignoreStaleRequest) {
          setPosts([...data.results]);
          setNext(data.next);
          console.log("Test post fetch");
        }
      })
      .catch((error) => {
        console.log(error);
      });

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  const postsList = posts.map((post) => (
    <li key={post.postid}>
      <Post url={post.url} />
    </li>
  ));

  const handleFetchPost = useCallback(() => {
    window.onbeforeunload = function scrollToTop() {
      window.scrollTo(0, 0);
    };
    let ignoreStaleRequest = false;
    console.log("Trying fetch");
    console.log(url);
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        if (!ignoreStaleRequest) {
          setPosts([...data.results]);
          setNext(data.next);
          console.log("Test post fetch");
        }
      })
      .catch((error) => {
        console.log(error);
      });

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  const handleFetchMorePost = useCallback(() => {
    fetch(next, {
      method: "GET",
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setPosts([...posts, ...data.results]);
        setNext(data.next);
      });
  }, [next, posts]);

  return (
    <InfiniteScroll
      dataLength={posts.length}
      next={handleFetchMorePost}
      hasMore={next !== ""}
      loader={<h4>Loading...</h4>}
      refreshFunction={handleFetchPost}
    >
      <ul> {postsList} </ul>
    </InfiniteScroll>
  );
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};
