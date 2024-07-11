import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import AuthConsumer from "../../components/AuthContext";
import InfinitePostsLayout from "../../components/InfinitePosts";

export function Feed() {
  const { isAuthenticated } = AuthConsumer();
  const navigate = useNavigate();
  const { feedName } = useParams();
  if (feedName == "home" && !isAuthenticated) {
    return navigate("/login");
  }
  useEffect(() => {
    document.title = `Threaddit | ${feedName}`
  }, [feedName])
  return <InfinitePostsLayout linkUrl={`posts/${feedName || "all"}`} apiQueryKey={feedName} />;
}

export default Feed;
