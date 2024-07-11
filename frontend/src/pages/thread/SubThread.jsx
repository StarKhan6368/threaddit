import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { AnimatePresence } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import AuthConsumer from "../../components/AuthContext";
import InfinitePostsLayout from "../../components/InfinitePosts";
import ManageMods from "../../components/ManageMods";
import Modal from "../../components/Modal";
import { NewThread } from "../../components/NewThread";
import Loader from "../../components/Loader";

export function SubThread() {
  const listRef = useRef();
  const navigate = useNavigate();
  const [modalData, setModalData] = useState(false);
  const queryClient = useQueryClient();
  const params = useParams();
  const { isAuthenticated, user } = AuthConsumer();
  const { data, isFetching } = useQuery({
    queryKey: ["thread", params.threadName],
    queryFn: async () => {
      return await axios.get(`/api/threads/${params.threadName}`).then((res) => res.data);
    },
  });
  useEffect(() => { document.title = "t/" + params.threadName; return () => { document.title = "Threaddit" } }, [params.threadName]);
  const threadData = data?.threadData;
  const { mutate } = useMutation({
    mutationFn: async (has_subscribed) => {
      if (has_subscribed) {
        axios.delete(`/api/threads/subscription/${threadData.id}`).then(() =>
          queryClient.setQueryData({ queryKey: ["thread", params.threadName] }, (oldData) => {
            return { threadData: { ...oldData.threadData, has_subscribed: false } };
          })
        );
      } else {
        axios.post(`/api/threads/subscription/${threadData.id}`).then(() =>
          queryClient.setQueryData({ queryKey: ["thread", params.threadName] }, (oldData) => {
            return { threadData: { ...oldData.threadData, has_subscribed: true } };
          })
        );
      }
    },
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
      case "logo":
        setModalData(
          <img src={threadData?.logo} className="object-cover w-11/12 max-h-5/6 md:w-max md:max-h-screen" alt="" />
        );
        break;
      default:
        navigate(`/u/${value}`);
    }
    listRef.current.value = "more";
  }
  return (
    <div className="flex flex-col flex-1 items-center w-full bg-theme-cultured">
      <div className="flex flex-col p-5 space-y-1 w-full bg-white rounded-md md:pb-3 md:space-y-3">
        {isFetching ? (
          <Loader forPosts={true} />
        ) : (
          <div
            className={`flex p-2 flex-col md:flex-row items-center rounded-md md:rounded-full bg-theme-cultured ${!threadData?.logo && "py-5"
              }`}>
            {threadData?.logo && (
              <img
                src={threadData?.logo}
                className="object-cover w-32 h-32 rounded-full cursor-pointer md:w-36 md:h-36"
                alt=""
                onClick={() => handleChange("logo")}
              />
            )}
            <div className="flex flex-col flex-1 justify-around items-center p-2 space-y-1">
              <div className="flex items-center space-x-5">
                <h1 className="text-xl font-semibold">{threadData?.name}</h1>
              </div>
              <p className="text-xs">Since: {new Date(threadData?.created_at).toDateString()}</p>
              {threadData?.description && (
                <p className={`text-center py-4 md:py-2 text-sm ${threadData?.description.length > 90 && "text-xs"}`}>
                  {threadData?.description}
                  {threadData?.description.length > 90 && "..."}
                </p>
              )}
              <div className="flex justify-between mt-2 space-x-7 w-full md:w-11/12">
                <p className="text-sm">{threadData?.subscriberCount} subscribers</p>
                <p className="text-sm">{threadData?.PostsCount} posts</p>
                <p className="text-sm">{threadData?.CommentsCount} comments</p>
              </div>
            </div>
          </div>
        )}
        <div className="flex flex-col justify-around space-y-3 md:space-x-10 md:flex-row md:space-y-0">
          {isAuthenticated && (
            <button
              className={`px-32 py-2 text-white rounded-full active:scale-90 ${threadData?.has_subscribed ? "bg-blue-400" : "bg-theme-red-coral"
                } `}
              onClick={() => mutate(threadData?.has_subscribed)}>
              {threadData?.has_subscribed ? "Leave" : "Join"}
            </button>
          )}
          <select
            ref={listRef}
            defaultValue={"more"}
            onChange={(e) => handleChange(e.target.value)}
            name="mods"
            id="mods"
            className="px-10 py-2 text-center rounded-md md:block bg-theme-cultured">
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
      </div>
      <InfinitePostsLayout
        apiQueryKey={threadData?.name}
        linkUrl={`posts/thread/${threadData?.id}`}
        enabled={threadData !== undefined}
      />
      <AnimatePresence>{modalData && <Modal setShowModal={setModalData}>{modalData}</Modal>}</AnimatePresence>
    </div>
  );
}

export default SubThread;
