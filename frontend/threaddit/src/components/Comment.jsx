import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { timeAgo } from "../pages/fullPost/utils";
import avatar from "../assets/avatar.png";
import Svg from "./Svg";
import Vote from "./Vote";
import { useState } from "react";
import Reply from "./Reply";
import Modal from "./Modal";
import AuthConsumer from "./AuthContext";

Comment.propTypes = {
  children: PropTypes.array,
  comment: PropTypes.object,
};

const borderColors = [
  "border-yellow-400",
  "border-blue-400",
  "border-purple-400",
  "border-green-400",
  "border-sky-400",
  "border-pink-400",
];

let curColor = 0;

export default function Comment({ children, comment }) {
  const { isAuthenticated } = AuthConsumer();
  const [showModal, setShowModal] = useState(false);
  const [modalData, setModaData] = useState(<></>);
  function onReplyClick() {
    if (isAuthenticated) {
      setShowModal(true);
      setModaData(
        <Reply className="w-5/6 h-5/6" parentComment={comment} isComment={true} setShowModal={setShowModal} />
      );
    } else {
      alert("You must be logged in to reply.");
    }
  }
  function colorSquence() {
    if (curColor == borderColors.length) {
      curColor = 0;
    }
    return borderColors[curColor++];
  }
  const timePassed = timeAgo(new Date(comment.comment_info.created_at));
  if (children.length > 0) {
    {
      return (
        <div className={`space-y-2 rounded-t-2xl border-l-2 ${colorSquence()}`}>
          <Comment key={comment.comment_info.id} {...{ children: [], comment }} />
          <ul className="ml-2 space-y-1">
            {children.map((child) => (
              <Comment key={child.comment.comment_info.id} {...child} />
            ))}
          </ul>
        </div>
      );
    }
  } else {
    return (
      <div className="px-1 py-2 space-y-2 w-full bg-white rounded-xl border-2 md:space-y-3 md:text-base">
        <div className="flex items-center space-x-2 text-sm font-medium">
          <img src={comment.user_info.user_avatar || avatar} alt="" className="w-5 h-5 rounded-full" />
          <Link to={`/u/${comment.user_info.user_name}`}>{comment.user_info.user_name}</Link>
          <p>{timePassed}</p>
        </div>
        <p className="ml-1 text-sm md:text-base">{comment.comment_info.content}</p>
        <div className="flex justify-around items-center space-x-5 md:justify-between md:mx-10">
          <div className="flex items-center space-x-1">
            <Svg type="share" className="w-5 h-5" />
            <p>Share</p>
          </div>
          <div className="flex items-center space-x-1">
            <Svg type="down-arrow" className="w-5 h-5" onClick={onReplyClick} />
            <p>Expand</p>
          </div>
          <div className="flex items-center space-x-1">
            <Svg type="comment" className="w-5 h-5" onClick={onReplyClick} />
            <p>Reply</p>
          </div>
          <div className="flex items-center space-x-2">
            <Vote
              {...{
                url: "/api/reactions/comment",
                intitalVote: comment.current_user?.has_upvoted,
                initialCount: comment.comment_info.comment_karma,
                contentID: comment.comment_info.id,
                type: "mobile",
              }}
            />
          </div>
        </div>
        {showModal && isAuthenticated && (
          <Modal showModal={showModal} setShowModal={setShowModal}>
            {modalData}
          </Modal>
        )}
      </div>
    );
  }
}
