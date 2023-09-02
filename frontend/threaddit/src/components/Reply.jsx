import { useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import PropTypes from "prop-types";
import { useState } from "react";
import { useParams } from "react-router-dom";
import avatar from "../assets/avatar.png";

Reply.propTypes = {
  parentComment: PropTypes.object,
  isComment: PropTypes.bool,
  setShowModal: PropTypes.func,
  edit: PropTypes.bool,
};
export default function Reply({ parentComment, isComment = false, setShowModal, edit = false }) {
  const queryClient = useQueryClient();
  const { postId } = useParams();
  const [reply, setReply] = useState("");
  async function handleSubmit(e) {
    e?.preventDefault();
    if (edit) {
      return axios.patch(`/api/comments/${parentComment.comment_info.id}`, { content: reply }).then(() => {
        setShowModal(false);
        queryClient.invalidateQueries({ queryKey: ["post/comment", postId] });
      });
    }
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
    <div className="flex flex-col justify-between p-5 w-5/6 bg-white rounded-md min-h-4/6 md:w-2/6">
      <div className="p-4 mx-auto space-y-3 w-full rouned-md">
        <div className="flex justify-center items-center p-2 space-x-5 w-full rounded-md border-2">
          <img src={parentComment.user_info.user_avatar || avatar} className="w-10 h-10 rounded-full" alt="" />
          <p>{parentComment.user_info.user_name}</p>
        </div>
        <div className="p-2">
          <p className="ml-2 text-sm italic">On {isComment ? "comment" : "post"} said</p>
          <p className="p-2 font-medium">
            {isComment ? parentComment.comment_info.content : parentComment.post_info.title}
          </p>
        </div>
      </div>
      <form className="flex-1 px-5 space-y-5" onSubmit={handleSubmit}>
        <label htmlFor="content" className="flex flex-col space-y-1">
          <span className="ml-2 text-sm font-semibold">{edit ? "Edit to" : "Reply"}</span>
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
