import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { AnimatePresence } from "framer-motion";
import { useParams } from "react-router-dom";
import Comment from "../../components/Comment";
import Post from "../../components/Post";
import ThreadsSidebar from "../../components/ThreadsSidebar";

export function FullPost() {
  const { postId } = useParams();
  const { data, isFetched } = useQuery({
    queryKey: ["post/comment", postId],
    queryFn: async () => await axios.get(`/api/comments/post/${postId}`).then((res) => res.data),
  });
  return (
    isFetched && (
      <div className="flex pb-20 md:pb-0">
        <ThreadsSidebar />
        <div className="flex flex-col p-2 space-y-2 w-full">
          <Post post={data?.post_info} isExpanded={true} />
          {data?.comment_info.length > 0 ? (
            <ul className="space-y-4 rounded-xl md:border-2 md:p-2 hover:shadow-sm border-theme-gray-blue">
              <AnimatePresence>
                {data?.comment_info.map((comment, index) => (
                  <Comment
                    key={comment.comment.comment_info.id}
                    {...comment}
                    postId={data?.post_info.thread_info.thread_id}
                    commentIndex={index}
                  />
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
        </div>
      </div>
    )
  );
}

export default FullPost;
