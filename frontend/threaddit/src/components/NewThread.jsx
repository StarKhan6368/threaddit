import AuthConsumer from "./AuthContext";
import avatar from "../assets/avatar.png";
import { useState } from "react";
import PropTypes from "prop-types";
import axios from "axios";

NewThread.propTypes = {
  subThreadName: PropTypes.string,
  setShowModal: PropTypes.func,
};

export function NewThread({ subThreadName, setShowModal }) {
  const [subName, setSubName] = useState(subThreadName);
  const [description, setDescription] = useState("");
  const [media, setMedia] = useState("");
  const [mediaType, setMediaType] = useState("image");
  const [imageUrl, setImageUrl] = useState("");
  const { user } = AuthConsumer();
  async function handleSubmit(e) {
    e?.preventDefault();
    const formData = new FormData();
    formData.append("name", `t/${subName}`);
    formData.append("content_type", mediaType);
    formData.append("content_url", imageUrl);
    formData.append("description", description);
    if (media) {
      formData.append("media", media, media.name);
    }
    await axios
      .post("/api/thread", formData, { headers: { "Content-Type": "multipart/form-data" } })
      .then(() => setShowModal(false))
      .catch((err) => alert(`${err.message} check your fields, Title is mandatory`));
  }
  return (
    <div className="flex flex-col p-5 space-y-5 w-5/6 rounded-md min-h-4/6 md:w-3/4 md:h-5/6 md:p-10 bg-theme-cultured">
      <div className="flex flex-col  justify-around items-center p-4 space-y-3 bg-white rounded-xl md:flex-row md:space-y-0">
        <p>Creating Subthread as</p>
        <div className="flex space-x-3 items-center">
          <img src={user.avatar || avatar} className="w-9 h-9 rounded-full" alt="" />
          <p>{user.username}</p>
        </div>
      </div>
      <form className="flex flex-col flex-1 justify-around p-3 space-y-5 w-full h-1/2 bg-white rounded-md">
        <label htmlFor="name" className="flex space-y-1 md:space-y-0 md:space-x-2 flex-col md:flex-row">
          <span className="text-sm font-light">Subthread Name</span>
          <input
            type="text"
            name="name"
            id="name"
            value={subName}
            placeholder={subName}
            onChange={(e) => setSubName(e.target.value)}
            className=" border-b w-full border-gray-800 focus:outline-none"
            required={true}
            maxLength={50}
          />
        </label>
        <label htmlFor="description" className="flex space-y-1 md:space-y-0 md:space-x-2 flex-col md:flex-row">
          <span className="text-sm font-light">Description</span>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            name="description"
            id="description"
            className="border-b w-full border-gray-800 focus:outline-none"
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
