import { useInfiniteQuery } from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import InfinitePostsLayout from "../../components/InfinitePosts";
import Spinner from "../../components/Spinner";

export default function SavedPosts() {
  const [duration, setDuration] = useState("alltime");
  const [sortBy, setSortBy] = useState("top");
  const { data, isFetching, fetchNextPage, hasNextPage } = useInfiniteQuery({
    queryKey: ["saved"],
    queryFn: async ({ pageParam = 0 }) => {
      return await axios.get(`/api/posts/saved?offset=${pageParam * 20}&limit=20`).then((res) => res.data);
    },
    getNextPageParam: (lastPage, pages) => {
      if (lastPage.length < 20) return undefined;
      return pages.length;
    },
  });
  if (isFetching) return <Spinner />;
  return (
    <div className="flex items-center p-2 w-full">
      <InfinitePostsLayout
        data={data}
        isFetching={isFetching}
        hasNextPage={hasNextPage}
        fetchNextpage={fetchNextPage}
        setSortBy={setSortBy}
        setDuration={setDuration}
        sortBy={sortBy}
        duration={duration}
        forSaved={true}
      />
    </div>
  );
}
