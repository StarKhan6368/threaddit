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
    <div className="flex flex-col flex-1 items-center p-2 w-full bg-theme-cultured">
      <div className="flex flex-col items-center w-full bg-theme-cultured">
        <div className="flex flex-col p-2 w-full bg-white rounded-md md:p-5">
          {!userIsFetching && data && (
            <div className="flex pr-3 py-0.5 pl-1 rounded-full bg-theme-cultured">
              <img src={data.avatar || avatar} className="w-24 h-24 bg-white rounded-full md:w-36 md:h-36" alt="" />
              <div className="flex flex-col flex-1 justify-around items-center pl-4 md:p-2">
                <h1 className="flex items-center space-x-2 text-lg font-semibold">
                  u/{data.username}{" "}
                  <span className="hidden text-sm font-light md:inline">- Created on: {data?.registrationDate}</span>
                </h1>
                <p className="hidden md:block">{data?.bio}</p>
                <div className="flex flex-col justify-between w-11/12 md:flex-row">
                  <div className="flex space-x-2 text-sm">
                    <p className="text-xs md:text-base">Total Posts: {data?.karma.posts_count}</p>
                    <p className="text-xs text-center md:text-base">Posts Karma: {data?.karma.posts_karma}</p>
                  </div>
                  <p className="text-xs md:text-base">Overall Karma: {data?.karma.user_karma}</p>
                  <div className="flex space-x-2 text-sm">
                    <p className="text-xs md:text-base">
                      <span className="hidden md:inline">Total </span>Comments: {data?.karma.comments_count}
                    </p>
                    <p className="text-xs md:text-base">Comments Karma: {data?.karma.comments_karma}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
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
