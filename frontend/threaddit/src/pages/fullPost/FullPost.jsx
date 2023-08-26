import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useParams } from "react-router-dom";
import ThreadsSidebar from "../../components/ThreadsSidebar";

export function FullPost() {
  const { postId } = useParams();
  const { data } = useQuery({
    queryKey: ["post", postId],
    queryFn: async () => await axios.get(`/api/post/${postId}`).then((res) => res.data),
  });
  console.log(data);
  return (
    <>
      <ThreadsSidebar />
    </>
  );
}

export default FullPost;
