import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import PropTypes from "prop-types";
import { useState } from "react";
import avatar from "../assets/avatar.png";
import AuthConsumer from "./AuthContext";
import Loader from "./Loader";

NewPost.propTypes = {
  setShowModal: PropTypes.func,
  isEdit: PropTypes.bool,
  postInfo: PropTypes.object,
  threadInfo: PropTypes.object,
};

export default function NewPost({ setShowModal, isEdit = false, postInfo = {}, threadInfo = {} }) {
  const { data, isLoading } = useQuery({
    queryKey: ["threads"],
    queryFn: async () => {
      return axios.get("/api/threads/get/all").then((res) => res.data);
    },
  });
  const queryClient = useQueryClient();
  const [title, setTitle] = useState(postInfo?.title || "");
  const [content, setContent] = useState(postInfo?.content || "");
  const [media, setMedia] = useState("");
  const [mediaType, setMediaType] = useState("media");
  const [imageUrl, setImageUrl] = useState("");
  const [thread, setThread] = useState(threadInfo.thread_id || 1);
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
    formData.append("subthread_id", thread);
    if (!isEdit) {
      await axios
        .post("/api/post", formData, { headers: { "Content-Type": "multipart/form-data" } })
        .then(() => setShowModal(false))
        .catch((err) => alert(`${err.message} check your fields, Title is mandatory`));
    } else {
      await axios
        .patch(`/api/post/${postInfo.id}`, formData, { headers: { "Content-Type": "multipart/form-data" } })
        .then((res) => {
          queryClient.setQueryData({ queryKey: ["post/comment", `${postInfo.id}`] }, (oldData) => {
            return { ...oldData, post_info: res.data.new_data };
          });
          setShowModal(false);
        })
        .catch((err) => alert(`${err.message} check your fields, Title is mandatory`));
    }
  });
  if (isLoading) return <Loader />;
  return (
    <div className="flex flex-col p-5 space-y-5 w-5/6 rounded-md blur-none min-h-4/6 md:w-3/4 md:h-5/6 md:p-10 bg-theme-cultured">
      <div className="flex flex-col justify-between items-center p-4 space-y-3 bg-white rounded-xl md:flex-row md:space-y-0">
        <div className="flex items-center space-x-3">
          <p>Posting as</p>
          <img src={user.avatar || avatar} className="object-cover w-8 h-8 rounded-full md:w-12 md:h-12" alt="" />
          <p>{user.username}</p>
        </div>
        {status === "loading" && <Loader forPosts={true} />}
        <div className="flex items-center space-x-2 md:space-x-3">
          <p className="hidden md:block">Posting on</p>
          <p className="md:hidden">On</p>
          <select
            name="thread"
            id="thread"
            className="px-3 py-2 bg-white rounded-md border md:px-12"
            value={thread}
            onChange={(e) => setThread(Number(e.target.value))}>
            {data?.map((thread) => (
              <option key={thread.name} value={thread.id}>
                {thread.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      <form
        encType="multipart/form-data"
        className="flex flex-col flex-1 justify-around p-3 space-y-5 w-full h-1/2 bg-white rounded-md">
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
        <label htmlFor="content">
          <span>Content</span>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            name="content"
            id="content"
            className="p-2 w-full max-h-28 border border-gray-800 focus:outline-none"
          />
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
