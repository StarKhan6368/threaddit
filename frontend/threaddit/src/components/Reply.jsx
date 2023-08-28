import axios from "axios";
import PropTypes from "prop-types";
import { useState } from "react";
import avatar from "../assets/avatar.png";
import AuthConsumer from "./AuthContext";
import { useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";

Reply.propTypes = {
  parentComment: PropTypes.object,
  isComment: PropTypes.bool,
  setShowModal: PropTypes.func,
};
export default function Reply({ parentComment, isComment = false, setShowModal }) {
  const queryClient = useQueryClient();
  const { postId } = useParams();
  const [reply, setReply] = useState("");
  const { user } = AuthConsumer();
  async function handleSubmit(e) {
    e?.preventDefault();
    const formData = new FormData();
    formData.append("content", reply);
    if (isComment) {
      formData.append("has_parent", true);
      formData.append("parent_id", parentComment.comment_info.id);
    }
    formData.append("post_id", postId);
    await axios.post("/api/comments", formData, { headers: { "Content-Type": "application/json" } }).then(() => {
      setShowModal(false);
      queryClient.invalidateQueries({ queryKey: ["post/comment", postId] });
    });
  }
  return (
    <div className="flex flex-col justify-between w-5/6 h-4/6 bg-white rounded-md md:h-5/6 md:w-1/2">
      <div className="flex flex-col justify-center items-center p-4 mt-5 space-x-3 space-y-5 md:flex-row md:space-y-0">
        <p className="text-xl">Commenting as</p>
        <div className="flex justify-center items-center p-2 space-x-5 w-full rounded-md border-2 md:w-fit">
          <img src={user.avatar || avatar} className="w-10 h-10 rounded-full" alt="" />
          <p className="text-xl">{user.username}</p>
        </div>
      </div>
      {isComment ? (
        <>
          <h4 className="mb-1 text-xl text-center">Replying To</h4>
          <div className="p-4 mx-auto space-y-3 w-full rouned-md">
            <div className="flex justify-center items-center p-2 space-x-5 w-full rounded-md border-2">
              <img src={parentComment.user_info.user_avatar || avatar} className="w-10 h-10 rounded-full" alt="" />
              <p>{parentComment.user_info.user_name}</p>
            </div>
            <div className="p-2">
              <p className="ml-2">Said</p>
              <p className="p-2 font-medium">{parentComment.comment_info.content}</p>
            </div>
          </div>
        </>
      ) : (
        <>
          <h4 className="mb-1 text-xl text-center">Replying To</h4>
          <div className="p-4 mx-auto space-y-3 w-full rouned-md">
            <div className="flex justify-center items-center p-2 space-x-5 w-full rounded-md border-2">
              <img src={parentComment.user_info.user_avatar || avatar} className="w-10 h-10 rounded-full" alt="" />
              <p>{parentComment.user_info.user_name}</p>
            </div>
            <div className="p-2">
              <p className="ml-2">On Post</p>
              <p className="p-2 font-medium">{parentComment.post_info.title}</p>
            </div>
          </div>
        </>
      )}
      <form className="flex-1 px-5 space-y-5" onSubmit={handleSubmit}>
        <label htmlFor="content" className="flex flex-col space-y-1">
          <span className="ml-2 text-sm font-semibold">Reply</span>
          <input
            autoFocus
            type="text"
            className="p-2 mx-2 rounded-md border-2 focus:outline-none"
            value={reply}
            onChange={(e) => setReply(e.target.value)}
          />
        </label>
        <button
          onClick={handleSubmit}
          className="px-12 py-2 w-full font-semibold text-white rounded-md bg-theme-orange active:scale-95">
          Submit
        </button>
      </form>
    </div>
  );
}
