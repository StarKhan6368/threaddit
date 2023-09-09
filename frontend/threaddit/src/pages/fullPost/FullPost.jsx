import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { AnimatePresence } from "framer-motion";
import { useParams } from "react-router-dom";
import Comment, { CommentMode } from "../../components/Comment";
import Post from "../../components/Post";
import ThreadsSidebar from "../../components/ThreadsSidebar";
import Loader from "../../components/Loader";
import { useState } from "react";
import AuthConsumer from "../../components/AuthContext";

export function FullPost() {
  const queryClient = useQueryClient();
  const { user } = AuthConsumer();
  const { postId } = useParams();
  const [commentMode, setCommentMode] = useState(false);
  const { data, isFetching } = useQuery({
    queryKey: ["post/comment", postId],
    queryFn: async () => await axios.get(`/api/comments/post/${postId}`).then((res) => res.data),
  });
  const { mutate } = useMutation({
    mutationFn: async (data) => {
      await axios.post(`/api/comments`, { post_id: postId, content: data }).then((res) => {
        queryClient.setQueryData({ queryKey: ["post/comment", postId] }, (oldData) => {
          return { ...oldData, comment_info: [...oldData.comment_info, res.data.new_comment] };
        });
        setCommentMode(false);
      });
    },
  });
  return isFetching ? (
    <Loader forPosts={true} />
  ) : (
    <div className="flex pb-20 md:pb-0">
      <ThreadsSidebar />
      <div className="flex flex-col p-2 space-y-2 w-full">
        <ul>
          <Post post={data?.post_info} isExpanded={true} setCommentMode={setCommentMode} />
        </ul>
        {commentMode && (
          <div className="py-3 pl-2 space-y-2 w-full bg-white rounded-xl md:text-base">
            <CommentMode
              user={user}
              defaultValue=""
              callBackSubmit={mutate}
              callBackCancel={() => setCommentMode(false)}
            />
          </div>
        )}
        <>
          {data?.comment_info.length > 0 ? (
            <ul className="space-y-2 rounded-xl md:border-2 md:p-2 hover:shadow-sm border-theme-gray-blue">
              <AnimatePresence>
                {data?.comment_info.map((comment, index) => (
                  <Comment key={comment.comment.comment_info.id} {...comment} commentIndex={index} />
                ))}
              </AnimatePresence>
            </ul>
          ) : (
            <div>
              <p className="p-5 text-sm bg-white rounded-xl border-2 md:text-base hover:shadow-sm border-theme-gray-blue">
                This post has no comments, be the first to reply!
              </p>
            </div>
          )}
        </>
      </div>
    </div>
  );
}

export default FullPost;
