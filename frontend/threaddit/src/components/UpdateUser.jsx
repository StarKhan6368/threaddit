import AuthConsumer from "./AuthContext";
import PropTypes from "prop-types";
import avatar from "../assets/avatar.png";
import { useEffect, useState } from "react";
import axios from "axios";
import { focusManager, useQueryClient } from "@tanstack/react-query";

UpdateUser.propTypes = {
  setModal: PropTypes.func,
};

export default function UpdateUser({ setModal }) {
  const queryClient = useQueryClient();
  const { user } = AuthConsumer();
  const [bio, setBio] = useState(user.bio);
  const [media, setMedia] = useState("");
  const [mediaType, setMediaType] = useState("image");
  const [imageUrl, setImageUrl] = useState("");
  async function handleSubmit(e) {
    e?.preventDefault();
    const formData = new FormData();
    formData.append("bio", bio);
    formData.append("content_type", mediaType);
    formData.append("content_url", imageUrl);
    if (media) {
      formData.append("avatar", media, media.name);
    }
    await axios
      .patch("/api/user", formData, { headers: { "Content-Type": "multipart/form-data" } })
      .then(() => {
        setModal(false);
        queryClient.invalidateQueries({ queryKey: ["user", user.username] });
      })
      .catch((err) => alert(`${err.message} check your fields`));
  }
  useEffect(() => {
    focusManager.setFocused(false);
    return () => focusManager.setFocused(true);
  }, []);
  return (
    <div className="flex flex-col p-5 space-y-5 w-5/6 rounded-md min-h-3/6 md:w-3/4 md:h-4/6 md:p-10 bg-theme-cultured">
      <div className="flex flex-col justify-between items-center p-4 space-y-3 bg-white rounded-xl md:flex-row md:space-y-0">
        <p>Updating Profile for</p>
        <img src={user.avatar || avatar} className="w-10 h-10 rounded-full md:w-14 md:h-14" alt="" />
        <p>{user.username}</p>
      </div>
      <form className="flex flex-col p-5 space-y-5 bg-white rounded-md" onSubmit={handleSubmit}>
        <label htmlFor="bio" className="flex flex-col p-2 md:space-x-3 md:flex-row">
          <span className="text-sm font-light">Bio</span>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            type="text"
            name="bio"
            id="bio"
            className="w-full h-20 max-h-28 border-b border-gray-800 focus:outline-none"
          />
        </label>
        <label htmlFor="media" className="flex flex-col items-center space-y-3 md:space-y-0 md:space-x-5 md:flex-row">
          <select
            className="px-10 py-2 bg-white rounded-md border md:px-12"
            name="type"
            id="media_type"
            onChange={(e) => setMediaType(e.target.value)}>
            <option value="image">Image</option>
            <option value="url">URL</option>
          </select>
          {mediaType === "image" ? (
            <input
              onChange={(e) => setMedia(e.target.files[0])}
              type="file"
              name="file"
              accept="image/*"
              id="image"
              className="w-full focus:outline-none"
            />
          ) : (
            <input
              type="text"
              name="media_url"
              id="media_url"
              className="p-2 w-full rounded-md border border-gray-800 focus:outline-none"
              onChange={(e) => setImageUrl(e.target.value)}
            />
          )}
        </label>
        <button
          onClick={handleSubmit}
          className="py-2 font-semibold text-white rounded-md bg-theme-orange active:scale-95">
          Submit
        </button>
      </form>
    </div>
  );
}
