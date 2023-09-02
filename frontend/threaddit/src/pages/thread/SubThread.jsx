import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import AuthConsumer from "../../components/AuthContext";
import InfinitePostsLayout from "../../components/InfinitePosts";
import ManageMods from "../../components/ManageMods";
import Modal from "../../components/Modal";
import { NewThread } from "../../components/NewThread";

export function SubThread() {
  const navigate = useNavigate();
  const [sortBy, setSortBy] = useState("top");
  const [modalData, setModalData] = useState(false);
  const queryClient = useQueryClient();
  const [duration, setDuration] = useState("alltime");
  const params = useParams();
  const { isAuthenticated, user } = AuthConsumer();
  const { data } = useQuery({
    queryKey: ["thread", params.threadName],
    queryFn: async () => {
      return await axios.get(`/api/threads/${params.threadName}`).then((res) => res.data);
    },
  });
  const threadData = data?.threadData;
  const {
    data: threadPosts,
    isFetching,
    fetchNextPage,
    hasNextPage,
  } = useInfiniteQuery({
    queryKey: ["thread", threadData?.id, "posts", sortBy, duration],
    queryFn: async ({ pageParam = 0 }) => {
      return await axios
        .get(
          `/api/posts/thread/${threadData?.id}?limit=${20}&offset=${
            pageParam * 20
          }&sortby=${sortBy}&duration=${duration}`
        )
        .then((res) => res.data);
    },
    getNextPageParam: (lastPage, pages) => {
      return lastPage.length === 20 ? pages.length : undefined;
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
  function handleChange(value) {
    switch (value) {
      case "more":
        break;
      case "edit":
        setModalData(<NewThread ogInfo={threadData} edit={true} setShowModal={setModalData} />);
        break;
      case "manage-mods":
        setModalData(<ManageMods mods={threadData.modList || []} threadId={threadData.id} />);
        break;
      default:
        navigate(`/u/${value}`);
    }
  }
  return (
    <div className="flex flex-col flex-1 items-center p-2 w-full bg-theme-cultured">
      <div className="flex flex-col p-5 space-y-5 w-full bg-white rounded-md">
        <div className={`flex pr-3 rounded-full bg-theme-cultured ${!threadData?.logo && "py-5"}`}>
          {threadData?.logo && <img src={threadData?.logo} className="w-24 h-24 rounded-full md:w-36 md:h-36" alt="" />}
          <div className="flex flex-col flex-1 justify-around items-center p-2">
            <div className="flex items-center space-x-5">
              <h1 className="text-lg font-semibold">{threadData?.name}</h1>
              <p className="hidden text-xs md:block">Since: {threadData?.created_at}</p>
            </div>
            <p className="text-xs md:hidden">Since: {new Date(threadData?.created_at).toDateString()}</p>
            <p className="hidden text-sm md:block">{threadData?.description}</p>
            <div className="flex flex-col justify-center md:space-x-3 md:flex-row">
              <p className="text-sm">{threadData?.subscriberCount} subscribers</p>
              <div className="flex justify-between space-x-3">
                <p className="text-sm">{threadData?.PostsCount} posts</p>
                <p className="text-sm">{threadData?.CommentsCount} comments</p>
              </div>
            </div>
          </div>
        </div>
        {isAuthenticated && (
          <div className="flex flex-col justify-around space-y-3 md:space-x-10 md:flex-row md:space-y-0">
            <button
              className={`px-32 py-2 text-white rounded-full active:scale-90 ${
                threadData?.has_subscribed ? "bg-blue-400" : "bg-theme-red-coral"
              } `}
              onClick={() => mutate(threadData?.has_subscribed)}>
              {threadData?.has_subscribed ? "Leave" : "Join"}
            </button>
            <select
              defaultValue={"more"}
              onChange={(e) => handleChange(e.target.value)}
              name="mods"
              id="mods"
              className="px-10 py-2 rounded-md md:block bg-theme-cultured">
              <option value={"more"}>More</option>
              {isAuthenticated && (user.mod_in.includes(threadData?.id) || user.roles.includes("admin")) && (
                <optgroup label="Subthread Options">
                  <option value="edit">Edit Subthread</option>
                  <option value="manage-mods">Manage Mods</option>
                </optgroup>
              )}
              <optgroup label="ModList">
                {threadData?.modList.map((mod) => (
                  <option key={mod} value={mod}>
                    {mod}
                  </option>
                ))}
              </optgroup>
            </select>
          </div>
        )}
      </div>
      <InfinitePostsLayout
        data={threadPosts}
        hasNextPage={hasNextPage}
        duration={duration}
        fetchNextpage={fetchNextPage}
        setDuration={setDuration}
        sortBy={sortBy}
        setSortBy={setSortBy}
        isFetching={isFetching}
      />
      {modalData && <Modal setShowModal={setModalData}>{modalData}</Modal>}
    </div>
  );
}

export default SubThread;
