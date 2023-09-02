import { useInfiniteQuery } from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import AuthConsumer from "../../components/AuthContext";
import InfinitePostsLayout from "../../components/InfinitePosts";
import ThreadsSidebar from "../../components/ThreadsSidebar";

export function Feed() {
  const { isAuthenticated } = AuthConsumer();
  const navigate = useNavigate();
  const params = useParams();
  const [sortBy, setSortBy] = useState("top");
  const [duration, setDuration] = useState("alltime");
  const { data, isFetching, fetchNextPage, hasNextPage } = useInfiniteQuery({
    queryKey: ["posts", params.feedName, sortBy, duration],
    queryFn: async ({ pageParam = 0 }) => {
      return await axios
        .get(`/api/posts/${params.feedName}?limit=${20}&offset=${pageParam * 20}&sortby=${sortBy}&duration=${duration}`)
        .then((data) => data.data);
    },
    getNextPageParam: (lastPage, pages) => {
      if (lastPage.length < 20) return undefined;
      return pages.length;
    },
  });

  if (params.feedName == "home" && !isAuthenticated) {
    return navigate("/login");
  }
  return (
    <>
      <main className="flex flex-1 max-w-full bg-theme-cultured">
        <ThreadsSidebar />
        <InfinitePostsLayout
          data={data}
          fetchNextpage={fetchNextPage}
          hasNextPage={hasNextPage}
          isFetching={isFetching}
          setSortBy={setSortBy}
          setDuration={setDuration}
          sortBy={sortBy}
          duration={duration}
        />
      </main>
    </>
  );
}

export default Feed;
