import PropTypes from "prop-types";
import { useState } from "react";
import { Link, ScrollRestoration } from "react-router-dom";
import avatar from "../assets/avatar.png";
import Modal from "./Modal";
import Svg from "./Svg";
import Vote from "./Vote";
import Reply from "./Reply";
import AuthConsumer from "./AuthContext";

Post.propTypes = {
  post: PropTypes.object,
  isExpanded: PropTypes.bool,
};

export function Post({ post, isExpanded = false }) {
  const { isAuthenticated } = AuthConsumer();
  const [modalShow, setShowModal] = useState(false);
  const [modalData, setModalData] = useState(<></>);
  function onImageClick() {
    if (post.post_info.media) {
      setShowModal(true);
      setModalData(
        <img className="w-11/12 max-h-5/6 md:w-max md:max-h-screen md:max-w-screen" src={post.post_info.media} alt="" />
      );
    }
  }
  function onReplyClick() {
    if (isAuthenticated) {
      setShowModal(true);
      setModalData(<Reply className="w-5/6 h-5/6" parentComment={post} setShowModal={setShowModal} />);
    } else {
      alert("You must be logged in to reply.");
    }
  }

  return (
    <>
      <div className="flex flex-col items-center p-1 pb-3 bg-white rounded-xl border-2 md:pb-0 hover:drop-shadow-md md:flex-row border-theme-gray-blue">
        <div className="flex flex-col flex-1 p-3 space-y-5 w-full h-full md:space-y-0 md:space-x-4 md:flex-row">
          {post.post_info.media && (
            <img
              onClick={() => onImageClick()}
              src={post.post_info.media}
              alt=""
              className="rounded-md duration-500 cursor-pointer md:h-32 md:w-32 hover:scale-110"
            />
          )}
          <div className="flex flex-col justify-between space-y-1 cursor-pointer">
            <div className={`flex flex-col  space-y-2 ${!isExpanded && "flex-1"}`}>
              <Link to={`/post/${post.post_info.id}`} className="flex-1 text-sm font-semibold md:text-lg text-ellipsis">
                {post.post_info.title}
              </Link>
              {isExpanded && <p className="text-sm">{post.post_info.content}</p>}
            </div>
            <div className="flex justify-between w-full md:space-x-2">
              <div className="flex space-x-2">
                <div className="flex items-center space-x-2 text-xs md:text-sm">
                  <Link to={`/u/${post.user_info.user_name}`}>
                    By <span className="font-medium">u/{post.user_info.user_name}</span>
                  </Link>
                  <img src={post.user_info.user_avatar || avatar} alt="" className="w-5 h-5 rounded-full" />
                </div>
                <div className="flex items-center space-x-2">
                  <p className="text-xs md:text-sm">in</p>
                  <Link
                    className="text-xs font-medium md:text-sm"
                    to={`/${post.thread_info.thread_name}`}>{` ${post.thread_info.thread_name}`}</Link>
                  <img src={post.thread_info.logo} alt="" className="w-5 h-5 rounded-full" />
                </div>
              </div>
              <p className="hidden text-sm font-light md:block">{post.post_info.created_at}</p>
            </div>
            <p className="text-sm font-light md:hidden">{post.post_info.created_at}</p>
          </div>
        </div>
        <div className="flex justify-around w-full h-full md:justify-evenly md:px-10 md:flex-col md:w-fit">
          {isExpanded ? (
            <div className="flex items-center space-x-1">
              <Svg type="comment" className="w-5 h-5" onClick={() => onReplyClick()} />
              <p>Reply</p>
            </div>
          ) : (
            <Link to={`/post/${post.post_info.id}`} className="flex items-center space-x-2 cursor-pointer group">
              <Svg type="comment" className="w-5 h-5" />
              <div className="flex space-x-1">
                <span className="text-sm cursor-pointer md:text-base">{post.post_info.comments_count}</span>
                <p className="hidden md:block">Comments</p>
              </div>
            </Link>
          )}
          <div className="hidden items-center space-x-2 cursor-pointer md:flex group">
            <Svg type="share" className="w-5 h-5" />
            <div className="flex space-x-1">
              <p className="text-sm cursor-pointer md:text-base">Share</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 cursor-pointer group">
            <Svg className="w-5 h-5" type="more" />
            <div className="flex space-x-1">
              <p className="text-sm cursor-pointer md:text-base">More</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 md:hidden">
            <Vote
              {...{
                intitalVote: post.current_user?.has_upvoted,
                initialCount: post.post_info.post_karma,
                url: "/api/reactions/post",
                contentID: post.post_info.id,
                type: "mobile",
              }}
            />
          </div>
        </div>
        <div className="hidden flex-col justify-around items-center my-2 space-y-1 w-28 border-l md:flex border-theme-gray-blue">
          <Vote
            {...{
              intitalVote: post.current_user?.has_upvoted,
              initialCount: post.post_info.post_karma,
              url: "/api/reactions/post",
              contentID: post.post_info.id,
              type: "full",
            }}
          />
        </div>
        <ScrollRestoration />
      </div>
      {modalShow && (
        <Modal setShowModal={setShowModal} showModal={modalShow}>
          {modalData}
        </Modal>
      )}
    </>
  );
}

export default Post;
