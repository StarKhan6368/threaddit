import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import { useParams } from "react-router-dom";
import PostLayout from "../../components/PostLayout";
import Spinner from "../../components/Spinner";
import AuthConsumer from "../../components/AuthContext";

export function SubThread() {
  const [sortBy, setSortBy] = useState("top");
  const queryClient = useQueryClient();
  const [duration, setDuration] = useState("alltime");
  const params = useParams();
  const { isAuthenticated } = AuthConsumer();
  const { data, isFetching: isThreadInfoFetching } = useQuery({
    queryKey: ["thread", params.threadName],
    queryFn: async () => {
      return await axios.get(`/api/threads/${params.threadName}`).then((res) => res.data);
    },
  });
  const threadData = data?.threadData;
  const { data: threadPosts, isFetching } = useQuery({
    queryKey: ["thread", threadData?.id, "posts", sortBy, duration],
    queryFn: async () => {
      return await axios
        .get(`/api/posts/thread/${threadData?.id}?limit=${20}&offset=${0}&sortby=${sortBy}&duration=${duration}`)
        .then((res) => res.data);
    },
    enabled: threadData?.id !== undefined,
  });
  const { mutate } = useMutation({
    mutationFn: async (has_subscribed) => {
      if (has_subscribed) {
        return await axios.delete(`/api/threads/subscription/${threadData.id}`).then((res) => res.data);
      } else {
        return await axios.post(`/api/threads/subscription/${threadData.id}`).then((res) => res.data);
      }
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["thread", params.threadName] }),
  });
  if (isFetching || isThreadInfoFetching) {
    return <Spinner />;
  }
  return (
    <div className="flex flex-col flex-1 items-center p-2 w-full bg-theme-cultured">
      <div className="flex flex-col p-5 space-y-5 w-full bg-white rounded-md">
        <div className="flex pr-3 rounded-full bg-theme-cultured">
          <img src={threadData.logo} className="w-24 h-24 rounded-full md:w-36 md:h-36" alt="" />
          <div className="flex flex-col flex-1 justify-around items-center p-2">
            <div className="flex space-x-5 items-center">
              <h1 className="text-lg font-semibold">{threadData.name}</h1>
              <p className="text-xs hidden md:block">Since: {threadData.created_at}</p>
            </div>
            <p className="text-xs md:hidden">Since: {new Date(threadData.created_at).toDateString()}</p>
            <p className="hidden text-sm md:block">{threadData.description}</p>
            <div className="flex space-x-3">
              <p className="text-sm">{threadData.subscriberCount} subscribers</p>
              <p className="text-sm">{threadData.PostsCount} posts</p>
              <p className="text-sm">{threadData.CommentsCount} comments</p>
            </div>
          </div>
        </div>
        {isAuthenticated && (
          <div className="flex justify-around md:space-x-10 flex-col md:flex-row space-y-3 md:space-y-0">
            <button
              className={`px-32 py-2 text-white rounded-full active:scale-90 ${
                threadData.has_subscribed ? "bg-blue-400" : "bg-theme-red-coral"
              } `}
              onClick={() => mutate(threadData.has_subscribed)}>
              {threadData.has_subscribed ? "Leave" : "Join"}
            </button>
            <select
              name="mods"
              id="mods"
              className="px-10 py-2 rounded-md md:block bg-theme-cultured"
              defaultValue={"ModList"}>
              <option value="ModList">ModList</option>
              {threadData.modList.map((mod) => (
                <option key={mod} value={mod}>
                  {mod}
                </option>
              ))}
            </select>
          </div>
        )}
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
