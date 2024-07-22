import { useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import PropTypes from "prop-types";
import { useState } from "react";
import { useParams } from "react-router-dom";

Comment.propTypes = {
  children: PropTypes.array,
  comment: PropTypes.object,
};

const borderColors = [
  "border-yellow-400",
  "border-blue-400",
  "border-purple-400",
  "border-green-400",
  "border-sky-400",
  "border-pink-400",
];

let curColor = 0;

export default function useComment({ children, comment }) {
  const queryClient = useQueryClient();
  const { postId } = useParams();
  const [commentChildren, setCommentChildren] = useState(children || []);
  const [{ comment_info: commentInfo, user_info: userInfo, current_user: currentUser }, setCommentInfo] =
    useState(comment);

  const { mutate: addComment } = useMutation({
    mutationFn: async (data) => {
      if (data.length === 0) {
        return;
      }
      await axios
        .post(
          "/api/comments",
          { post_id: postId, content: data, has_parent: true, parent_id: comment.comment_info.id },
          { headers: { "Content-Type": "application/json" } }
        )
        .then((res) => {
          setCommentChildren([...commentChildren, res.data.new_comment]);
        });
    },
  });

  const { mutate: deleteComment } = useMutation({
    mutationFn: async (childId = null) => {
      if (window.confirm("Are you sure you want to delete this comment?")) {
        axios.delete(`/api/comments/${childId || commentInfo.id}`).then(() => {
          if (childId) {
            setCommentChildren(commentChildren.filter((c) => c.comment.comment_info.id !== childId));
          } else {
            queryClient.setQueryData(["post/comment", postId], (oldData) => {
              return {
                ...oldData,
                comment_info: oldData.comment_info.filter((c) => c.comment.comment_info.id !== commentInfo.id),
              };
            });
          }
        });
      }
    },
  });

  const { mutate: updateComment } = useMutation({
    mutationFn: async (data) => {
      if (data.length === 0) {
        return;
      }
      await axios.patch(`/api/comments/${commentInfo.id}`, { content: data }).then(() => {
        setCommentInfo({
          user_info: userInfo,
          current_user: currentUser,
          comment_info: { ...commentInfo, content: data, is_edited: true },
        });
      });
    },
  });

  function colorSquence() {
    if (curColor == borderColors.length) {
      curColor = 0;
    }
    return borderColors[curColor++];
  }

  return {
    commentChildren,
    commentInfo,
    userInfo,
    currentUser,
    addComment,
    deleteComment,
    updateComment,
    colorSquence,
  };
}
