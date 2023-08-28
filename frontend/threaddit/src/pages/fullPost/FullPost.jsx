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
    <div className="flex">
      <ThreadsSidebar />
      <div className="flex flex-col p-2 space-y-2 w-full">
        <Post post={data.post_info} isExapaned={true} />
        <ul className="space-y-4 rounded-xl border-2 hover:shadow-sm border-theme-gray-blue">
          {data.comment_info.map((comment) => (
            <Comment key={comment.comment.comment_info.id} {...comment} />
          ))}
        </ul>
      </div>
    </div>
  );
}

export default FullPost;
