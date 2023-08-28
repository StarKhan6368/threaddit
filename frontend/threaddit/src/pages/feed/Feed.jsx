import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import { useParams } from "react-router-dom";
import PostLayout from "../../components/PostLayout";
import ThreadsSidebar from "../../components/ThreadsSidebar";

export function Feed() {
  const params = useParams();
  const [sortBy, setSortBy] = useState("top");
  const [duration, setDuration] = useState("alltime");
  const { data, isFetching } = useQuery({
    queryKey: ["posts", params.feedName, sortBy, duration],
    queryFn: async () => {
      return await axios
        .get(`/api/posts/${params.feedName}?limit=${20}&offset=${0}&sortby=${sortBy}&duration=${duration}`)
        .then((data) => data.data);
    },
  });
  return (
    <main className="flex flex-1 max-w-full bg-theme-cultured">
      <ThreadsSidebar />
      <PostLayout
        data={data}
        isFetching={isFetching}
        setSortBy={setSortBy}
        setDuration={setDuration}
        sortBy={sortBy}
        duration={duration}
      />
    </main>
  );
}

export default Feed;
