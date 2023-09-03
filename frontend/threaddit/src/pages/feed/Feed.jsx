import { useNavigate, useParams } from "react-router-dom";
import AuthConsumer from "../../components/AuthContext";
import InfinitePostsLayout from "../../components/InfinitePosts";
import ThreadsSidebar from "../../components/ThreadsSidebar";

export function Feed() {
  const { isAuthenticated } = AuthConsumer();
  const navigate = useNavigate();
  const params = useParams();
  if (params.feedName == "home" && !isAuthenticated) {
    return navigate("/login");
  }
  return (
    <main className="flex flex-1 max-w-full bg-theme-cultured">
      <ThreadsSidebar />
      <InfinitePostsLayout linkUrl={`posts/${params.feedName}`} apiQueryKey={params.feedName} />
    </main>
  );
}

export default Feed;
