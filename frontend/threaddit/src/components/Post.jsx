import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import PropTypes from "prop-types";
import { useState } from "react";
import useAuthContext from "../components/AuthContext";
import Svg from "./Svg";

Post.propTypes = {
  post: PropTypes.object,
};

export function Post({ post }) {
  const [vote, setVote] = useState(post.current_user.has_upvoted);
  const [voteCount, setVoteCount] = useState(post.post_info.post_karma);
  const { isAuthenticated } = useAuthContext();
  const { mutate } = useMutation({
    mutationFn: ({ vote, method, postId }) => {
      switch (method) {
        case "put":
          return axios.put(`/api/reactions/post/${postId}`, { is_upvote: vote }).then((res) => res.data);
        case "patch":
          return axios.patch(`/api/reactions/post/${postId}`, { is_upvote: vote }).then((res) => res.data);
        case "delete":
          return axios.delete(`/api/reactions/post/${postId}`).then((res) => res.data);
        default:
          break;
      }
    },
  });
  function handleVote(newVote) {
    if (!isAuthenticated) {
      return alert("You must be logged in to vote.");
    }
    if (vote === null) {
      mutate({ vote: newVote, method: "put", postId: post.post_info.id });
      setVoteCount((voteCount) => voteCount + (newVote ? 1 : -1));
    } else if (newVote === null) {
      mutate({ vote: newVote, method: "delete", postId: post.post_info.id });
      setVoteCount((voteCount) => voteCount - (vote ? 1 : -1));
    } else {
      mutate({ vote: newVote, method: "patch", postId: post.post_info.id });
      setVoteCount((voteCount) => voteCount + (newVote ? 2 : -2));
    }
    setVote(newVote);
  }
  return (
    <div className="flex flex-col items-center rounded-xl border hover:shadow-sm md:flex-row border-theme-gray-blue p-0.5">
      <div className="flex flex-col flex-1 p-5 space-y-5 h-full md:space-y-0 md:space-x-4 md:flex-row">
        {post.post_info.media && (
          <img
            src={post.post_info.media}
            alt=""
            className="w-full h-full rounded-md duration-500 md:h-28 md:w-28 hover:scale-110"
          />
        )}
        <div className="flex flex-col flex-1 justify-between space-y-3 h-full cursor-pointer">
          <h3 className="text-lg font-semibold text-ellipsis">{post.post_info.title}</h3>
          <div className="flex justify-between">
            <div className="flex items-center text-sm font-medium md:space-x-2">
              <p>Posted by u/{post.user_info.user_name}</p>
              <img src={post.user_info.user_avatar} alt="" className="w-5 h-5 rounded-full" />
              <p>
                in <span>{post.thread_info.thread_name}</span>
              </p>
              <img src={post.thread_info.logo} alt="" className="w-5 h-5 rounded-full" />
            </div>
            <p className="hidden text-sm font-light md:block">{post.post_info.created_at}</p>
          </div>
          <p className="text-sm font-light md:hidden">{post.post_info.created_at}</p>
        </div>
      </div>
      <div className="flex justify-evenly m-5 w-full h-full md:flex-col md:w-fit">
        <div className="flex items-center space-x-2 cursor-pointer group">
          <Svg type="comment" className="w-5 h-5" />
          <div className="flex space-x-1">
            <span>{post.post_info.comments_count}</span>
            <p>Comments</p>
          </div>
        </div>
        <div className="hidden md:flex items-center space-x-2 cursor-pointer group">
          <Svg type="share" className="w-5 h-5" />
          <div className="flex space-x-1">
            <span></span>
            <p>Share</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 cursor-pointer group">
          <Svg className="w-5 h-5" type="more" />
          <div className="flex space-x-1">
            <p>More</p>
          </div>
        </div>
        <div className="flex items-center md:hidden space-x-3">
          <Svg
            className="w-8 h-8"
            type="mobileVote"
            defaultStyle={true}
            onClick={() => handleVote(!vote ? true : null)}
            active={vote === true}
          />
          <p className="text-lg font-semibold">
            <span>{voteCount}</span>
          </p>
          <Svg
            className="w-8 h-8 rotate-180"
            type="mobileVote"
            defaultStyle={false}
            onClick={() => handleVote(vote === false ? null : false)}
            active={vote === false}
          />
        </div>
      </div>
      <div className="hidden flex-col justify-around items-center my-3 w-28 h-full border-l md:flex border-theme-gray-blue">
        <div className="px-5 py-1 bg-orange-100 rounded-md">
          <Svg
            type="down-arrow"
            defaultStyle={true}
            className="w-10 h-10 rotate-180"
            onClick={() => handleVote(!vote ? true : null)}
            active={vote === true}
          />
        </div>
        <p className="text-lg font-semibold">
          <span>{voteCount}</span>
        </p>
        <div className="px-5 py-1 bg-blue-50 rounded-md group">
          <Svg
            type="down-arrow"
            className="w-10 h-10"
            defaultStyle={false}
            onClick={() => handleVote(vote === false ? null : false)}
            active={vote === false}
          />
        </div>
      </div>
    </div>
  );
}

export default Post;
