import { useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import Markdown from "markdown-to-jsx";
import PropTypes from "prop-types";
import { useState } from "react";
import avatar from "../assets/avatar.png";
import AuthConsumer from "./AuthContext";
import Loader from "./Loader";
import { ThreadSearch } from "./Navbar";
import Svg from "./Svg";

NewPost.propTypes = {
  setShowModal: PropTypes.func,
  isEdit: PropTypes.bool,
  postInfo: PropTypes.object,
  threadInfo: PropTypes.object,
};

export default function NewPost({ setShowModal, isEdit = false, postInfo = {}, threadInfo = {} }) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState(postInfo?.title || "");
  const [content, setContent] = useState(postInfo?.content || "");
  const [media, setMedia] = useState("");
  const [preMd, setPreMd] = useState(false);
  const [mediaType, setMediaType] = useState("media");
  const [imageUrl, setImageUrl] = useState("");
  const [thread, setThread] = useState(isEdit ? { id: threadInfo.thread_id, name: threadInfo.thread_name } : false);
  const { user } = AuthConsumer();
  const { mutate: handleSubmit, status } = useMutation(async (e) => {
    e?.preventDefault();
    const formData = new FormData();
    formData.append("title", title);
    formData.append("content_type", mediaType);
    formData.append("content_url", imageUrl);
    formData.append("content", content);
    if (media) {
      formData.append("media", media, media.name);
    }
    formData.append("subthread_id", thread.id);
    if (!isEdit) {
      await axios
        .post("https://threaddit.onrender.com/api/post", formData, { headers: { "Content-Type": "multipart/form-data" } })
        .then(() => setShowModal(false))
        .catch((err) => alert(`${err.message} check your fields, Title is mandatory`));
    } else {
      await axios
        .patch(`https://threaddit.onrender.com/api/post/${postInfo.id}`, formData, { headers: { "Content-Type": "multipart/form-data" } })
        .then((res) => {
          queryClient.setQueryData({ queryKey: ["post/comment", `${postInfo.id}`] }, (oldData) => {
            return { ...oldData, post_info: res.data.new_data };
          });
          setShowModal(false);
        })
        .catch((err) => alert(`${err.message} check your fields, Title is mandatory`));
    }
  });
  return (
    <div className="flex flex-col p-5 space-y-5 w-5/6 h-4/6 rounded-md blur-none md:w-3/4 md:h-5/6 md:p-10 bg-theme-cultured">
      <div className="flex flex-col justify-between items-center p-4 space-y-3 bg-white rounded-xl md:flex-row md:space-y-0">
        <div className="flex items-center space-x-3">
          <p>{isEdit ? "Editing" : "Posting"} as</p>
          <img src={user.avatar || avatar} className="object-cover w-8 h-8 rounded-full md:w-12 md:h-12" alt="" />
          <p>{user.username}</p>
        </div>
        {status === "loading" && <Loader forPosts={true} />}
        <div className="flex items-center mr-2 space-x-2 md:space-x-3">
          <p className="hidden md:block">{isEdit ? "Editing" : "Posting"} on</p>
          <p className="md:hidden">On</p>
          {thread ? (
            <div className="flex items-center p-1 space-x-3">
              <p className="tracking-wide medium text- md:text-base text-theme-orange">{thread.name}</p>
              <Svg type="delete" className="w-7 h-7 text-theme-orange" onClick={() => setThread(false)} />
            </div>
          ) : (
            <ThreadSearch callBackFunc={setThread} forPost={true} />
          )}
        </div>
      </div>
      <form
        encType="multipart/form-data"
        className="flex flex-col flex-1 justify-around p-1.5 w-full h-1/2 bg-white rounded-md">
        <label htmlFor="title">
          <span>Title</span>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            type="text"
            name="title"
            id="title"
            className="w-full border-b border-gray-800 focus:outline-none"
            required
          />
        </label>
        <label htmlFor="content" className="">
          <span>{preMd ? "Markdown Preview" : "Content"}</span>
          <button
            type="button"
            className="active:scale-90 ml-5 my-0.5 py-0.5 px-2 bg-blue-600 text-white font-semibold rounded-md"
            onClick={() => setPreMd(!preMd)}>
            {preMd ? "close preview" : "preview markdown"}
          </button>
          <div className="flex flex-col space-y-2">
            {preMd ? (
              <div className="overflow-auto p-2 max-w-full h-28 border border-gray-800 prose">
                <Markdown options={{ forceBlock: true, wrapper: "div" }} className="w-full">
                  {content.replace("\n", "<br />\n") || "This is markdown preview"}
                </Markdown>
              </div>
            ) : (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                name="content"
                id="content"
                className="p-2 w-full h-28 border border-gray-800 md:max-h-32 focus:outline-none"
              />
            )}
          </div>
        </label>
        <label htmlFor="media" className="flex flex-col items-center space-y-3 md:space-y-0 md:space-x-5 md:flex-row">
          <select
            className="px-10 py-2 bg-white rounded-md border md:px-12"
            name="mediaType"
            id="mediaType"
            onChange={(e) => setMediaType(e.target.value)}>
            <option value="media">Media</option>
            <option value="url">URL</option>
          </select>
          {mediaType === "media" ? (
            <label htmlFor="media">
              <input
                onChange={(e) => {
                  if (e.target.files[0].size > 10485760) {
                    alert("File too large, only upload files less than 10MB");
                  } else {
                    setMedia(e.target.files[0]);
                  }
                }}
                type="file"
                name="media"
                alt="media"
                accept="image/*, video/*"
                id="media"
                className="w-full focus:outline-none"
              />
            </label>
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
        {isEdit && (
          <span className="text-sm font-semibold text-red-500">
            Only Add Image if you want to modify the original image if empty the original will be used.
          </span>
        )}
        <button
          onClick={handleSubmit}
          disabled={status === "loading"}
          className="py-2 font-semibold text-white rounded-md bg-theme-orange active:scale-95">
          {status === "loading" ? "Submitting..." : "Submit"}
        </button>
      </form>
    </div>
  );
}
