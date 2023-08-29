import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useParams } from "react-router-dom";
import ThreadsSidebar from "../../components/ThreadsSidebar";
import Post from "../../components/Post";
import Spinner from "../../components/Spinner";
import Comment from "../../components/Comment";

export function FullPost() {
  const { postId } = useParams();
  const { data, isLoading } = useQuery({
    queryKey: ["post/comment", postId],
    queryFn: async () => await axios.get(`/api/comments/post/${postId}`).then((res) => res.data),
  });
  if (isLoading) return <Spinner />;
  return (
    <div className="flex pb-20 md:pb-0">
      <ThreadsSidebar />
      <div className="flex flex-col p-2 space-y-2 w-full">
        <Post post={data.post_info} isExpanded={true} />
        {data.comment_info.length > 0 ? (
          <ul className="space-y-4 rounded-xl md:border-2 md:p-2 hover:shadow-sm border-theme-gray-blue">
            {data.comment_info.map((comment) => (
              <Comment key={comment.comment.comment_info.id} {...comment} />
            ))}
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
  );
}

export default FullPost;
