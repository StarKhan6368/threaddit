import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import Spinner from "../../components/Spinner";
import PostLayout from "../../components/PostLayout";
import { useState } from "react";

export default function SavedPosts() {
  const [duration, setDuration] = useState("alltime");
  const [sortBy, setSortBy] = useState("top");
  const { data, isFetching } = useQuery({
    queryKey: ["saved"],
    queryFn: async () => {
      return await axios.get("/api/posts/saved").then((res) => res.data);
    },
  });
  if (isFetching) return <Spinner />;
  return (
    <div className="p-2 w-full flex items-center">
      <PostLayout
        data={data}
        isFetching={isFetching}
        setSortBy={setSortBy}
        setDuration={setDuration}
        sortBy={sortBy}
        duration={duration}
      />
    </div>
  );
}
