import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import avatar from "../../assets/avatar.png";
import AuthConsumer from "../../components/AuthContext";
import InfinitePostsLayout from "../../components/InfinitePosts";
import Modal from "../../components/Modal";
import UpdateUser from "../../components/UpdateUser";
import { Chat } from "../inbox/Inbox";
import Loader from "../../components/Loader";

export function Profile() {
  const { logout, user } = AuthConsumer();
  const { username } = useParams();
  const [action, setAction] = useState(false);
  const { data, isFetching: userIsFetching } = useQuery({
    queryKey: ["user", username],
    queryFn: async () => {
      return await axios.get(`/api/user/${username}`).then((res) => res.data);
    },
  });
  useEffect(() => {
    switch (action) {
      case "message":
        setAction(<Chat sender={data} setCurChat={setAction} newChat={true} />);
        break;
      case "edit":
        setAction(<UpdateUser setModal={setAction} />);
        break;
      case "delete":
        if (window.confirm("Are you sure you want to delete your account?")) {
          axios.delete(`/api/user`).then(() => logout());
        }
        setAction(false);
        break;
    }
  }, [action, data, username, logout]);
  return (
    <div className="flex flex-col flex-1 items-center w-full bg-theme-cultured">
      {userIsFetching ? (
        <Loader forPosts={true} />
      ) : (
        <div className="flex flex-col items-center w-full bg-theme-cultured">
          <div className="flex flex-col p-2 w-full bg-white rounded-md md:p-5">
            <div className="flex flex-col flex-1 justify-between items-center p-2 w-full rounded-md md:flex-row md:rounded-full bg-theme-cultured">
              <img
                src={data.avatar || avatar}
                className="object-cover w-24 h-24 bg-white rounded-full cursor-pointer md:w-36 md:h-36"
                alt=""
                onClick={() =>
                  setAction(
                    <img
                      src={data.avatar || avatar}
                      className="object-cover w-11/12 max-h-5/6 md:w-max md:max-h-screen"
                      alt=""
                    />
                  )
                }
              />
              <div className="flex flex-col flex-1 items-center w-full md:p-2">
                <h1 className="mt-2 text-lg font-semibold md:m-0">u/{data.username}</h1>
                <p className="my-4 w-11/12 text-sm text-center md:my-2 md:text-base">{data?.bio}</p>
                <div className="flex justify-between items-center w-full md:w-11/12">
                  <p className="text-xs md:text-sm">Karma: {data?.karma.user_karma}</p>
                  <p className="text-xs md:text-sm">Cake Day On: {new Date(data?.registrationDate).toDateString()}</p>
                </div>
              </div>
            </div>
            <div className="flex flex-col my-2 text-sm md:text-sm">
              <div className="flex justify-between space-x-2">
                <p className="">Total Posts: {data?.karma.posts_count}</p>
                <p className="">Posts Karma: {data?.karma.posts_karma}</p>
              </div>

              <div className="flex justify-between space-x-2">
                <p className="">Total Comments: {data?.karma.comments_count}</p>
                <p className="">Comments Karma: {data?.karma.comments_karma}</p>
              </div>
            </div>
            <select
              name="options"
              id="options"
              className="p-2 mt-2 bg-white rounded-md border-2"
              value={action}
              onChange={(e) => setAction(e.target.value)}>
              <option value={false}>Choose an action</option>
              {user.username === data?.username && (
                <>
                  <option value="edit">Update Profile</option>
                  <option value="delete">Delete Account</option>
                </>
              )}
              <option value="message">Message</option>
            </select>
          </div>
        </div>
      )}
      <InfinitePostsLayout
        apiQueryKey={data?.username}
        linkUrl={`posts/user/${data?.username}`}
        enabled={data?.username !== undefined}
      />
      <AnimatePresence>
        {action !== false && action !== "delete" && (
          <Modal showModal={action} setShowModal={setAction}>
            {action}
          </Modal>
        )}
      </AnimatePresence>
    </div>
  );
}

export default Profile;
