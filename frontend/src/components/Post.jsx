import { AnimatePresence, motion, useInView } from "framer-motion";
import PropTypes from "prop-types";
import { useEffect, useRef, useState } from "react";
import ReactPlayer from "react-player";
import { Link, ScrollRestoration, useNavigate } from "react-router-dom";
import avatar from "../assets/avatar.png";
import AuthConsumer from "./AuthContext";
import Modal from "./Modal";
import PostMoreOptions from "./PostMoreOptions";
import Svg from "./Svg";
import Vote from "./Vote";
import Markdown from "markdown-to-jsx";

Post.propTypes = {
  post: PropTypes.object,
  isExpanded: PropTypes.bool,
  postIndex: PropTypes.number,
  setCommentMode: PropTypes.func,
};

export function Post({ post, isExpanded = false, postIndex, setCommentMode }) {
  const navigate = useNavigate();
  const { isAuthenticated } = AuthConsumer();
  const vidRef = useRef(null);
  const inView = useInView(vidRef, { amount: "all" });
  const [modalShow, setShowModal] = useState(false);
  const [modalData, setModalData] = useState(<></>);
  useEffect(() => {
    if (isExpanded) {
      document.title = post.post_info.title;
    }
    return () => {
      if (isExpanded) {
        document.title = "Threaddit";
      }
    }
  }, [isExpanded])
  function onMediaClick(mediaType) {
    if (post?.post_info.media) {
      setShowModal(true);
      if (mediaType === "video") {
        setModalData(<ReactPlayer playing controls url={post?.post_info.media} />);
      } else {
        setModalData(
          <img className="object-cover w-11/12 max-h-5/6 md:w-max md:max-h-screen" src={post?.post_info.media.replace("additional_args", "c_auto,g_auto")} alt="" />
        );
      }
    }
  }
  function onReplyClick() {
    if (isAuthenticated) {
      setCommentMode((data) => !data);
    } else {
      alert("You must be logged in to reply.");
    }
  }
  const PostVariant = {
    hidden: {
      opacity: 0,
      y: 100,
    },
    animate: {
      opacity: 1,
      y: 0,
    },
    empty: {},
  };
  function isImage(url) {
    return /(jpg|jpeg|png|webp|avif|gif|svg|image)/.test(url);
  }
  async function handleShare() {
    return navigator.clipboard
      .writeText(`${location.host}/post/${post?.post_info.id}`)
      .then(() => {
        alert("Copied Post Link to clipboard");
      })
      .catch((err) => alert(err));
  }
  const createdAt = new Date(post?.post_info.created_at);
  return (
    <>
      <motion.li
        className={`flex flex-col p-1 pb-3 bg-white rounded-xl border-2 md:pb-0 hover:drop-shadow-md ${!isExpanded && "md:flex-row"
          } border-theme-gray-blue`}
        variants={PostVariant}
        initial={postIndex < 5 || isExpanded ? "hidden" : "empty"}
        animate={postIndex < 5 || isExpanded ? "animate" : "empty"}
        exit={{ opacity: 0, y: 100, transition: { duration: 0.25 } }}
        transition={{
          duration: 0.25,
          delay: postIndex * 0.25,
        }}>
        {post.post_info.media && (
          <div
            className={`relative overflow-hidden ${isExpanded ? "h-full md:h-96" : "md:w-64 md:h-32"} md:pt-0 ${!isImage(post.post_info.media) && "pt-[56.25%] aspect-video"
              } rounded-md my-auto bg-black`}
            ref={vidRef}>
            {!isImage(post.post_info.media) ? (
              <ReactPlayer
                url={post.post_info.media}
                width="100%"
                height="100%"
                controls
                loading="lazy"
                muted={!isExpanded}
                loop
                playing={vidRef.current && vidRef.current.offsetWidth > 256 && inView}
                style={{ position: "absolute", top: 0, left: 0 }}
              />
            ) : (
              <img
                onClick={() => onMediaClick("image")}
                loading="lazy" width="auto" height="100%"
                src={post.post_info.media}
                alt=""
                className={`object-cover w-full h-full rounded-md duration-500 md:cursor-pointer ${!isExpanded && "hover:scale-105"
                  }`}
              />
            )}
          </div>
        )}
        <div className="flex flex-col flex-1 p-3 space-y-5 w-full md:space-y-0 md:space-x-4 md:flex-row">
          <div className="flex flex-col space-y-1 w-full md:justify-between">
            {isExpanded ? (
              <div className="flex flex-col space-y-2 w-full h-full">
                <div className={`w-full font-semibold text-ellipsis ${post.post_info.content && "border-b-2 pb-2"}`}>
                  {post?.post_info.title}
                </div>
                {post.post_info.content && (
                  <div className="max-w-full text-black prose prose-sm md:prose-base prose-blue">
                    <Markdown className="[&>*:first-child]:mt-0">{post?.post_info.content}</Markdown>
                  </div>
                )}
              </div>
            ) : (
              <Link to={`/post/${post?.post_info.id}`} className="flex flex-col space-y-2 w-full h-full">
                <div className="w-full font-semibold text-ellipsis">{post?.post_info.title}</div>
              </Link>
            )}
            <div className="flex justify-between items-center">
              <div className="flex space-x-2 w-full md:w-fit">
                <div className="flex items-center space-x-2 text-xs">
                  <Link to={`/u/${post?.user_info.user_name}`}>
                    By{" "}
                    <span className="text-xs font-medium text-blue-600 hover:underline">
                      u/{post?.user_info.user_name}
                    </span>
                  </Link>
                  <img
                    src={post?.user_info.user_avatar || avatar}
                    alt=""
                    className="object-cover w-6 h-6 rounded-full"
                  />
                </div>
                <div className="flex items-center space-x-2 ">
                  <p className="text-xs">in</p>
                  <Link
                    to={`/${post?.thread_info.thread_name}`}
                    className="text-xs font-medium hover:underline text-theme-orange">{` ${post?.thread_info.thread_name}`}</Link>
                  {post?.thread_info.thread_logo && (
                    <img src={post?.thread_info.thread_logo} alt="" className="object-cover w-6 h-6 rounded-full" />
                  )}
                </div>
                <span onClick={() => navigate(`/post/${post?.post_info.id}`)} className="flex-1 md:hidden"></span>
              </div>
              <div className="hidden space-x-1 md:flex">
                <p className="text-xs font-light">
                  {createdAt.toDateString()} {createdAt.toLocaleTimeString({ hour12: true })}
                </p>
                <p className="text-xs">{post?.post_info.is_edited && "Edited"}</p>
              </div>
            </div>
            <div className="flex space-x-1 md:hidden">
              <p className="text-xs font-light">
                {createdAt.toDateString()} {createdAt.toLocaleTimeString({ hour12: true })}
              </p>
              <p className="text-xs">{post?.post_info.is_edited && "Edited"}</p>
            </div>
          </div>
        </div>
        <div className={`flex ${isExpanded && "items-center justify-between mx-5 md:-mt-4"}`}>
          <div
            className={`flex justify-around w-full md:w-fit md:justify-evenly  ${!isExpanded ? "md:flex-col md:px-10" : "space-x-10"
              }`}>
            {isExpanded ? (
              <div className="flex items-center space-x-1">
                <Svg type="comment" className="w-4 h-4 md:w-5 md:h-5" onClick={() => onReplyClick()} />
                <p className="text-sm md:cursor-pointer md:text-base">Reply</p>
              </div>
            ) : (
              <Link to={`/post/${post?.post_info.id}`} className="flex items-center space-x-2 md:cursor-pointer group">
                <Svg type="comment" className="w-4 h-4 md:w-5 md:h-5" />
                <div className="flex space-x-1">
                  <span className="text-sm md:text-base">{post?.post_info.comments_count}</span>
                  <p className="hidden md:block">Comments</p>
                </div>
              </Link>
            )}
            <div className="hidden items-center space-x-2 md:cursor-pointer md:flex group" onClick={handleShare}>
              <Svg type="share" className="w-4 h-4 md:w-5 md:h-5" />
              <p className="text-sm md:cursor-pointer md:text-base">Share</p>
            </div>
            <PostMoreOptions
              creatorInfo={post?.user_info}
              threadInfo={post?.thread_info}
              postInfo={post?.post_info}
              setShowModal={setShowModal}
              setModalData={setModalData}
              handleShare={handleShare}
              currentUser={post?.current_user}
            />
            <div className="flex items-center space-x-3 md:hidden">
              <Vote
                {...{
                  intitalVote: post?.current_user?.has_upvoted,
                  initialCount: post?.post_info.post_karma,
                  url: "https://threaddit.onrender.com/api/reactions/post",
                  contentID: post?.post_info.id,
                  type: "mobile",
                }}
              />
            </div>
          </div>
          <div
            className={`hidden justify-around items-center my-2 space-y-1  md:flex border-theme-gray-blue ${isExpanded ? "flex-row space-x-10" : "flex-col px-5 border-l"
              }`}>
            <Vote
              {...{
                intitalVote: post?.current_user?.has_upvoted,
                initialCount: post?.post_info.post_karma,
                url: "/api/reactions/post",
                contentID: post?.post_info.id,
                type: "full",
              }}
            />
          </div>
        </div>
      </motion.li>
      {isExpanded && <ScrollRestoration />}
      <AnimatePresence>
        {modalShow && (
          <Modal setShowModal={setShowModal} showModal={modalShow}>
            {modalData}
          </Modal>
        )}
      </AnimatePresence>
    </>
  );
}

export default Post;
