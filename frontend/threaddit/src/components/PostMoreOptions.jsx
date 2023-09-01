import { useRef, useState } from "react";
import Svg from "./Svg";
import useClickOutside from "../hooks/useClickOutside";
import AuthConsumer from "./AuthContext";
import PropTypes from "prop-types";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";

MoreOptions.propTypes = {
  creatorInfo: PropTypes.object,
  threadInfo: PropTypes.object,
  postInfo: PropTypes.object,
};

export default function MoreOptions({ creatorInfo, threadInfo, postInfo }) {
  const { isAuthenticated, user } = AuthConsumer();
  const [postSaved, setPostSaved] = useState(postInfo.saved);
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
      await axios.delete(`/api/post/${postInfo.id}`);
      if (location.pathname.includes("post")) {
        return navigate(-1);
      } else {
        return navigate(0);
      }
    } else {
      alert("You must be logged in to delete.");
    }
  }
  async function handleSaved() {
    if (postSaved) {
      await axios.delete(`/api/posts/saved/${postInfo.id}`);
      setPostSaved(false);
    } else {
      await axios.put(`/api/posts/saved/${postInfo.id}`);
      setPostSaved(true);
    }
    queryClient.invalidateQueries({ queryKey: ["saved"] });
  }
  const shouldBeAbleToDelete =
    isAuthenticated &&
    (creatorInfo.user_name === user.username ||
      user.roles.includes("admin") ||
      (user.roles.includes("mod") && user.mod_in.includes(threadInfo.thread_id)));
  return (
    <div ref={myRef} className="flex relative items-center cursor-pointer group" onClick={() => setExpand(true)}>
      <Svg className="w-4 h-4 md:w-6 md:h-6" type="more" />
      <p className="ml-2 text-sm cursor-pointer md:text-base">More</p>
      {expand && (
        <ul className="absolute top-full p-1 mt-1 space-y-1 w-24 list-none bg-white rounded-md border-2 border-theme-cultured">
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
        </ul>
      )}
    </div>
  );
}
