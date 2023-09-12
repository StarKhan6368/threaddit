import { useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import PropTypes from "prop-types";
import { useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import useClickOutside from "../hooks/useClickOutside";
import AuthConsumer from "./AuthContext";
import NewPost from "./NewPost";
import Svg from "./Svg";

MoreOptions.propTypes = {
  creatorInfo: PropTypes.object,
  threadInfo: PropTypes.object,
  currentUser: PropTypes.object,
  postInfo: PropTypes.object,
  setShowModal: PropTypes.func,
  setModalData: PropTypes.func,
  handleShare: PropTypes.func,
};

export default function MoreOptions({
  creatorInfo,
  threadInfo,
  currentUser,
  postInfo,
  setShowModal,
  setModalData,
  handleShare,
}) {
  const { isAuthenticated, user } = AuthConsumer();
  const [postSaved, setPostSaved] = useState(currentUser?.saved);
  const queryClient = useQueryClient();
  const location = useLocation();
  const navigate = useNavigate();
  const myRef = useRef();
  const [expand, setExpand] = useState(false);
  useClickOutside(myRef, () => {
    setExpand(false);
  });
  async function handleDelte() {
    if (isAuthenticated) {
      await axios.delete(`/api/post/${postInfo?.id}`);
      if (location.pathname.includes("post")) {
        return navigate(-1);
      }
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    } else {
      alert("You must be logged in to delete.");
    }
    setExpand(false);
  }
  async function handleSaved() {
    if (!isAuthenticated) {
      return alert("You must be logged in to save.");
    }
    if (postSaved) {
      await axios.delete(`/api/posts/saved/${postInfo?.id}`);
      setPostSaved(false);
    } else {
      await axios.put(`/api/posts/saved/${postInfo?.id}`);
      setPostSaved(true);
    }
    queryClient.invalidateQueries({ queryKey: ["saved"] });
    setExpand(false);
  }
  function handleEdit() {
    setShowModal(true);
    setModalData(<NewPost isEdit={true} postInfo={postInfo} setShowModal={setShowModal} threadInfo={threadInfo} />);
  }
  const shouldBeAbleToDelete =
    isAuthenticated &&
    (creatorInfo.user_name === user.username ||
      user.roles.includes("admin") ||
      (user.roles.includes("mod") && user.mod_in.includes(threadInfo.thread_id)));
  return (
    <>
      <div ref={myRef} className="flex relative items-center cursor-pointer group" onClick={() => setExpand(true)}>
        <Svg className="w-4 h-4 md:w-6 md:h-6" type="more" />
        <p className="ml-2 text-sm cursor-pointer md:text-base">More</p>
        {expand && (
          <ul className="absolute top-full z-20 p-1 mt-1 space-y-1 w-24 list-none bg-white rounded-md border-2 border-theme-cultured">
            <li className="p-1 text-sm cursor-pointer md:text-base hover:bg-theme-cultured" onClick={handleSaved}>
              {postSaved ? "Unsave" : "Save"}
            </li>
            {shouldBeAbleToDelete && (
              <li
                className="p-1 text-sm text-red-500 cursor-pointer md:text-base hover:bg-theme-cultured"
                onClick={handleDelte}>
                Delete
              </li>
            )}
            {creatorInfo.user_name === user.username && (
              <li onClick={handleEdit} className="p-1 text-sm cursor-pointer md:text-base hover:bg-theme-cultured">
                Edit
              </li>
            )}
            <li
              className="p-1 text-sm cursor-pointer md:hidden md:text-base hover:bg-theme-cultured"
              onClick={() => {
                handleShare().then(() => setExpand(false));
              }}>
              Share
            </li>
          </ul>
        )}
      </div>
    </>
  );
}
