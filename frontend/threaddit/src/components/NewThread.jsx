import AuthConsumer from "./AuthContext";
import avatar from "../assets/avatar.png";
import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import axios from "axios";
import { focusManager, useQueryClient } from "@tanstack/react-query";

NewThread.propTypes = {
  subThreadName: PropTypes.string,
  setShowModal: PropTypes.func,
  edit: PropTypes.bool,
  ogInfo: PropTypes.object,
};

export function NewThread({ subThreadName, setShowModal, edit = false, ogInfo = {} }) {
  const queryClient = useQueryClient();
  const [subName, setSubName] = useState(edit ? ogInfo.name : subThreadName);
  const [description, setDescription] = useState(ogInfo?.description || "");
  const [media, setMedia] = useState("");
  const [mediaType, setMediaType] = useState("image");
  const [imageUrl, setImageUrl] = useState("");
  const { user } = AuthConsumer();
  async function handleSubmit(e) {
    e?.preventDefault();
    const formData = new FormData();
    if (!edit) {
      formData.append("name", `t/${subName}`);
    }
    formData.append("content_type", mediaType);
    formData.append("content_url", imageUrl);
    formData.append("description", description);
    if (media) {
      formData.append("media", media, media.name);
    }
    if (!edit) {
      await axios
        .post("/api/thread", formData, { headers: { "Content-Type": "multipart/form-data" } })
        .then(() => setShowModal(false))
        .catch((err) => alert(`${err.message} check your fields`));
    } else {
      await axios
        .patch(`/api/thread/${ogInfo.id}`, formData, { headers: { "Content-Type": "multipart/form-data" } })
        .then((res) => {
          setShowModal(false);
          queryClient.setQueryData({ queryKey: ["thread", `${ogInfo.name.slice(2)}`] }, () => res.data.new_data);
        })
        .catch((err) => alert(`${err.message} check your fields`));
    }
  }
  useEffect(() => {
    focusManager.setFocused(false);
    return () => focusManager.setFocused(true);
  }, []);
  return (
    <div
      className={`flex flex-col p-5 space-y-5 w-5/6 rounded-md min-h-4/6 ${
        edit ? "md:w-2/4 md:h-4/6" : "md:w-3/4 md:h-5/6"
      }  md:p-10 bg-theme-cultured`}>
      <div className="flex flex-col justify-around items-center p-4 space-y-3 bg-white rounded-xl md:flex-row md:space-y-0">
        <p>{edit ? "Editing" : "Creating"} Subthread as</p>
        <div className="flex items-center space-x-3">
          <img src={user.avatar || avatar} className="object-cover w-9 h-9 rounded-full" alt="" />
          <p>{user.username}</p>
        </div>
      </div>
      <form className="flex flex-col flex-1 justify-around p-3 space-y-5 w-full h-1/2 bg-white rounded-md">
        {!edit && (
          <label htmlFor="name" className="flex flex-col space-y-1 md:space-y-0 md:space-x-2 md:flex-row">
            <span className="text-sm font-light">Subthread Name</span>
            <input
              type="text"
              name="name"
              id="name"
              value={subName}
              placeholder={subName}
              onChange={(e) => setSubName(e.target.value)}
              className="w-full border-b border-gray-800 focus:outline-none"
              required={true}
              maxLength={50}
            />
          </label>
        )}
        <label
          htmlFor="description"
          className="flex flex-col items-center space-y-1 md:space-y-0 md:space-x-2 md:flex-row">
          <span className="text-sm font-light">Description</span>
          <textarea
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            name="description"
            id="description"
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
              onChange={(e) => {
                if (e.target.files[0].size > 10485760) {
                  alert("File too large, only upload files less than 10MB");
                } else {
                  setMedia(e.target.files[0]);
                }
              }}
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
        {edit && (
          <span className="text-sm font-semibold text-red-500">
            Only Add Image if you want to modify the original image if empty the original will be used.
          </span>
        )}
        <button
          onClick={handleSubmit}
          className="py-2 font-semibold text-white rounded-md bg-theme-orange active:scale-95">
          Submit
        </button>
      </form>
    </div>
  );
}
