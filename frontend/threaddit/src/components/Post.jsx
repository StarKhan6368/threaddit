import PropTypes from "prop-types";
import { useState } from "react";
import { Link } from "react-router-dom";
import avatar from "../assets/avatar.png";
import Modal from "./Modal";
import Svg from "./Svg";
import Vote from "./Vote";
import Reply from "./Reply";
import AuthConsumer from "./AuthContext";

Post.propTypes = {
  post: PropTypes.object,
  isExapaned: PropTypes.bool,
};

export function Post({ post, isExapaned = false }) {
  const { isAuthenticated } = AuthConsumer();
  const [modalShow, setShowModal] = useState(false);
  const [modalData, setModalData] = useState(<></>);
  function onImageClick() {
    if (post.post_info.media) {
      setShowModal(true);
      setModalData(<img className="w-11/12" src={post.post_info.media} alt="" />);
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
    <div className="flex flex-col items-center p-1 pb-3 bg-white rounded-xl border-2 md:pb-0 hover:shadow-sm md:flex-row border-theme-gray-blue">
      <div className="flex flex-col flex-1 p-3 space-y-5 w-full h-full md:space-y-0 md:space-x-4 md:flex-row">
        {post.post_info.media && (
          <img
            onClick={() => onImageClick()}
            src={post.post_info.media}
            alt=""
            className="w-full h-full rounded-md border-8 duration-500 cursor-pointer md:border-none border-theme-gray-blue md:h-32 md:w-32 hover:scale-110"
          />
        )}
        <div className="flex flex-col flex-1 justify-between space-y-3 cursor-pointer">
          <div className="flex flex-col flex-1 space-y-5">
            <Link to={`/post/${post.post_info.id}`} className="flex-1 text-lg font-semibold text-ellipsis">
              {post.post_info.title}
            </Link>
            {isExapaned && <p className="text-sm">{post.post_info.content}</p>}
          </div>
          <div className="flex justify-between w-full md:space-x-2">
            <div className="flex flex-col md:flex-row">
              <div className="flex items-center text-sm font-medium md:space-x-2">
                <Link to={`/u/${post.user_info.user_name}`}>Posted by u/{post.user_info.user_name}</Link>
                <img src={post.user_info.user_avatar || avatar} alt="" className="w-5 h-5 rounded-full" />
              </div>
              <div className="flex items-center space-x-1">
                <p>in</p>
                <Link to={`/${post.thread_info.thread_name}`}>{` ${post.thread_info.thread_name}`}</Link>
                <img src={post.thread_info.logo} alt="" className="w-5 h-5 rounded-full" />
              </div>
            </div>
            <p className="hidden text-sm font-light md:block">{post.post_info.created_at}</p>
          </div>
          <p className="text-sm font-light md:hidden">{post.post_info.created_at}</p>
        </div>
      </div>
      <div className="flex justify-evenly w-full h-full md:mx-5 md:flex-col md:w-fit">
        {isExapaned ? (
          <div className="flex items-center space-x-1">
            <Svg type="comment" className="w-5 h-5" onClick={() => onReplyClick()} />
            <p>Reply</p>
          </div>
        ) : (
          <Link to={`/post/${post.post_info.id}`} className="flex items-center space-x-2 cursor-pointer group">
            <Svg type="comment" className="w-5 h-5" />
            <div className="flex space-x-1">
              <span>{post.post_info.comments_count}</span>
              <p>Comments</p>
            </div>
          </Link>
        )}
        <div className="hidden items-center space-x-2 cursor-pointer md:flex group">
          <Svg type="share" className="w-5 h-5" />
          <div className="flex space-x-1">
            <p>Share</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 cursor-pointer group">
          <Svg className="w-5 h-5" type="more" />
          <div className="flex space-x-1">
            <p>More</p>
          </div>
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
      {modalShow && (
        <Modal setShowModal={setShowModal} showModal={modalShow}>
          {modalData}
        </Modal>
      )}
    </div>
  );
}

export default Post;
