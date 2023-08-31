import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import { useParams } from "react-router-dom";
import avatar from "../../assets/avatar.png";
import Modal from "../../components/Modal";
import PostLayout from "../../components/PostLayout";
import Spinner from "../../components/Spinner";
import Svg from "../../components/Svg";
import { Chat } from "../inbox/Inbox";

export function Profile() {
  const { username } = useParams();
  const [showModal, setShowModal] = useState(false);
  const [sortBy, setSortBy] = useState("top");
  const [duration, setDuration] = useState("alltime");
  const { data, isFetching: userIsFetching } = useQuery({
    queryKey: ["user", username],
    queryFn: async () => {
      return await axios.get(`/api/user/${username}`).then((res) => res.data);
    },
  });
  const { data: userPosts, isFetching } = useQuery({
    queryKey: ["user", data?.username, "posts", sortBy, duration],
    queryFn: async () => {
      return await axios
        .get(`/api/posts/user/${data?.username}?limit=${20}&offset=${0}&sortby=${sortBy}&duration=${duration}`)
        .then((res) => res.data);
    },
    enabled: data?.username !== undefined,
  });
  return (
    <div className="flex flex-col flex-1 items-center p-2 w-full bg-theme-cultured">
      <div className="flex flex-col items-center w-full bg-theme-cultured">
        <div className="flex flex-col p-2 w-full bg-white rounded-md md:p-5">
          {!userIsFetching && (
            <div className="flex pr-3 py-0.5 pl-1 rounded-full bg-theme-cultured">
              <img src={data?.avatar || avatar} className="w-24 h-24 bg-white rounded-full md:w-36 md:h-36" alt="" />
              <div className="flex flex-col flex-1 justify-around items-center pl-4 md:p-2">
                <h1 className="flex items-center space-x-2 text-lg font-semibold">
                  u/{data.username}{" "}
                  <span className="hidden text-sm font-light md:inline">- Created on: {data.registrationDate}</span>
                  <Svg
                    type="mail"
                    className="w-5 h-5"
                    active={true}
                    defaultStyle={false}
                    onClick={() => setShowModal(true)}
                  />
                </h1>
                <p className="hidden md:block">{data.bio}</p>
                <div className="flex flex-col justify-between w-11/12 md:flex-row">
                  <div className="flex space-x-2 text-sm">
                    <p className="text-xs md:text-base">Total Posts: {data.karma.posts_count}</p>
                    <p className="text-xs text-center md:text-base">Posts Karma: {data.karma.posts_karma}</p>
                  </div>
                  <p className="text-xs md:text-base">Overall Karma: {data.karma.user_karma}</p>
                  <div className="flex space-x-2 text-sm">
                    <p className="text-xs md:text-base">
                      <span className="hidden md:inline">Total </span>Comments: {data.karma.comments_count}
                    </p>
                    <p className="text-xs md:text-base">Comments Karma: {data.karma.comments_karma}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      {!isFetching ? (
        <PostLayout
          data={userPosts}
          duration={duration}
          setDuration={setDuration}
          sortBy={sortBy}
          setSortBy={setSortBy}
          isFetching={isFetching}
        />
      ) : (
        <Spinner />
      )}
      {showModal && (
        <Modal showModal={showModal} setShowModal={setShowModal}>
          <Chat sender={{ name: data.username }} setCurChat={setShowModal} newChat={true} />
        </Modal>
      )}
    </div>
  );
}

export default Profile;
