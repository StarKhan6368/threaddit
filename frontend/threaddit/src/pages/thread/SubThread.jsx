import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import { useParams } from "react-router-dom";
import PostLayout from "../../components/PostLayout";
import Spinner from "../../components/Spinner";

export function SubThread() {
  const [sortBy, setSortBy] = useState("top");
  const [duration, setDuration] = useState("alltime");
  const params = useParams();
  const { data: threadData, isFetching: isThreadInfoFetching } = useQuery({
    queryKey: ["thread", params.threadName],
    queryFn: async () => {
      return await axios.get(`/api/threads/${params.threadName}`).then((res) => res.data);
    },
  });
  const threadId = threadData?.subthreadData?.id;
  const { data: threadPosts, isFetching } = useQuery({
    queryKey: ["thread", threadId, "posts", sortBy, duration],
    queryFn: async () => {
      return await axios
        .get(`/api/posts/thread/${threadId}?limit=${20}&offset=${0}&sortby=${sortBy}&duration=${duration}`)
        .then((res) => res.data);
    },
    enabled: threadData?.subthreadData?.id !== undefined,
  });
  if (isFetching || isThreadInfoFetching) {
    return <Spinner />;
  }
  return (
    <div className="flex flex-col flex-1 items-center p-5 max-w-full bg-theme-cultured">
      <div className="w-full bg-white rounded-md">
        <p>{threadData.name}</p>
        <p>{threadData.subscriberCount}</p>
      </div>
      <PostLayout
        data={threadPosts}
        duration={duration}
        setDuration={setDuration}
        sortBy={sortBy}
        setSortBy={setSortBy}
        isFetching={isFetching}
      />
    </div>
  );
}

export default SubThread;
