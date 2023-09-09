import { AnimatePresence, motion } from "framer-motion";
import PropTypes from "prop-types";
import { useState } from "react";
import { Link, ScrollRestoration, useNavigate } from "react-router-dom";
import avatar from "../assets/avatar.png";
import AuthConsumer from "./AuthContext";
import Modal from "./Modal";
import PostMoreOptions from "./PostMoreOptions";
import Svg from "./Svg";
import Vote from "./Vote";

Post.propTypes = {
  post: PropTypes.object,
  isExpanded: PropTypes.bool,
  postIndex: PropTypes.number,
  setCommentMode: PropTypes.func,
};

export function Post({ post, isExpanded = false, postIndex, setCommentMode }) {
  const navigate = useNavigate();
  const { isAuthenticated } = AuthConsumer();
  const [modalShow, setShowModal] = useState(false);
  const [modalData, setModalData] = useState(<></>);
  function onImageClick() {
    if (post?.post_info.media) {
      setShowModal(true);
      setModalData(<img className="w-11/12 max-h-5/6 md:w-max md:max-h-screen" src={post?.post_info.media} alt="" />);
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
        className="flex flex-col p-1 pb-3 bg-white rounded-xl border-2 md:pb-0 hover:drop-shadow-md md:flex-row border-theme-gray-blue"
        variants={PostVariant}
        initial={postIndex < 5 || isExpanded ? "hidden" : "empty"}
        animate={postIndex < 5 || isExpanded ? "animate" : "empty"}
        exit={{ opacity: 0, y: 100, transition: { duration: 0.25 } }}
        transition={{
          duration: 0.25,
          delay: postIndex * 0.25,
        }}>
        <div className="flex flex-col flex-1 p-3 space-y-5 w-full md:space-y-0 md:space-x-4 md:flex-row">
          {post?.post_info.media && (
            <img
              onClick={() => onImageClick()}
              src={post?.post_info.media}
              alt=""
              className="rounded-md duration-500 cursor-pointer md:h-32 md:w-32 hover:scale-110"
            />
          )}
          <div className="flex flex-col md:justify-between space-y-1 w-full md:cursor-pointer">
            <Link to={`/post/${post?.post_info.id}`} className="flex flex-col space-y-2 w-full h-full">
              <div className="w-full text-sm font-semibold md:text-lg text-ellipsis">{post?.post_info.title}</div>
              {isExpanded && <p className="text-sm">{post?.post_info.content}</p>}
            </Link>
            <div className="flex justify-between md:space-x-2">
              <div className="flex space-x-2 w-full md:w-fit">
                <div className="flex items-center space-x-2 text-xs md:text-sm">
                  <Link to={`/u/${post?.user_info.user_name}`}>
                    By{" "}
                    <span className="hover:underline hover:text-blue-600 font-medium text-xs  md:text-sm">
                      u/{post?.user_info.user_name}
                    </span>
                  </Link>
                  <img src={post?.user_info.user_avatar || avatar} alt="" className="w-6 h-6 rounded-full" />
                </div>
                <div className="flex items-center space-x-2">
                  <p className="text-xs md:text-sm">in</p>
                  <Link
                    to={`/${post?.thread_info.thread_name}`}
                    className="hover:underline hover:text-theme-orange font-medium text-xs  md:text-sm">{` ${post?.thread_info.thread_name}`}</Link>
                  {post?.thread_info.thread_logo && (
                    <img src={post?.thread_info.thread_logo} alt="" className="w-6 h-6 rounded-full" />
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
        <div className="flex justify-around w-full md:justify-evenly md:px-10 md:flex-col md:w-fit">
          {isExpanded ? (
            <div className="flex items-center space-x-1">
              <Svg type="comment" className="w-4 h-4 md:w-6 md:h-6" onClick={() => onReplyClick()} />
              <p className="text-sm cursor-pointer md:text-base">Reply</p>
            </div>
          ) : (
            <Link to={`/post/${post?.post_info.id}`} className="flex items-center space-x-2 cursor-pointer group">
              <Svg type="comment" className="w-4 h-4 md:w-6 md:h-6" />
              <div className="flex space-x-1">
                <span className="text-sm cursor-pointer md:text-base">{post?.post_info.comments_count}</span>
                <p className="hidden md:block">Comments</p>
              </div>
            </Link>
          )}
          <div className="hidden items-center space-x-2 cursor-pointer md:flex group" onClick={handleShare}>
            <Svg type="share" className="w-4 h-4 md:w-6 md:h-6" />
            <p className="text-sm cursor-pointer md:text-base">Share</p>
          </div>
          <PostMoreOptions
            creatorInfo={post?.user_info}
            threadInfo={post?.thread_info}
            postInfo={post?.post_info}
            setShowModal={setShowModal}
            setModalData={setModalData}
            handleShare={handleShare}
          />
          <div className="flex items-center space-x-3 md:hidden">
            <Vote
              {...{
                intitalVote: post?.current_user?.has_upvoted,
                initialCount: post?.post_info.post_karma,
                url: "/api/reactions/post",
                contentID: post?.post_info.id,
                type: "mobile",
              }}
            />
          </div>
        </div>
        <div className="hidden flex-col justify-around items-center my-2 space-y-1 w-28 border-l md:flex border-theme-gray-blue">
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
