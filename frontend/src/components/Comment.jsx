import { AnimatePresence, motion } from "framer-motion";
import PropTypes from "prop-types";
import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import avatar from "../assets/avatar.png";
import useComment from "../hooks/useComment";
import { timeAgo } from "../pages/fullPost/utils";
import AuthConsumer from "./AuthContext";
import Svg from "./Svg";
import Vote from "./Vote";
import Markdown from "markdown-to-jsx";

Comment.propTypes = {
  children: PropTypes.array,
  comment: PropTypes.object,
  threadID: PropTypes.string,
  commentIndex: PropTypes.number,
  parentDelete: PropTypes.func,
};

export default function Comment({ children, comment, threadID, commentIndex, parentDelete = null }) {
  const listRef = useRef(null);
  const [isReply, setIsReply] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [expandChildren, setExpandChildren] = useState(false);
  const {
    commentChildren,
    commentInfo,
    userInfo,
    currentUser,
    addComment,
    deleteComment,
    updateComment,
    colorSquence,
  } = useComment({
    children,
    comment,
  });
  const { isAuthenticated, user } = AuthConsumer();
  const timePassed = timeAgo(new Date(commentInfo.created_at));
  function handleSelect(value) {
    switch (value) {
      case "delete":
        if (parentDelete) {
          parentDelete(commentInfo.id);
        } else {
          deleteComment();
        }
        listRef.current.value = "more";
        break;
      case "edit":
        setEditMode(true);
        break;
      case "share":
        navigator.clipboard.writeText(window.location.href);
        alert("Post Link Copied to Clipboard");
        listRef.current.value = "more";
        break;
    }
  }
  return (
    <motion.li
      className={`py-3 pl-2 space-y-2 w-full bg-white rounded-xl md:text-base ${!parentDelete && "border"}`}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: commentIndex * 0.15 }}
      exit={{ opacity: 0, y: -10, transition: { duration: 0.1 } }}>
      {editMode ? (
        <CommentMode
          callBackSubmit={(data) => {
            updateComment(data);
            setEditMode(false);
            listRef.current.value = "more";
          }}
          callBackCancel={() => {
            setEditMode(false);
            listRef.current.value = "more";
          }}
          defaultValue={commentInfo.content}
          user={user}
        />
      ) : (
        <>
          <div className="flex items-center space-x-2 text-sm font-medium">
            <img loading="lazy" width="auto" height="100%" src={userInfo.user_avatar || avatar} alt="" className="object-cover w-5 h-5 rounded-full" />
            <Link to={`/u/${userInfo.user_name}`} className="font-medium text-blue-600 hover:underline">
              {userInfo.user_name}
            </Link>
            <p>{timePassed}</p>
            <p>{commentInfo.is_edited && "Edited"}</p>
          </div>
          <div className="max-w-full text-black prose prose-sm md:prose-base prose-blue">
            <Markdown className="[&>*:first-child]:mt-0">{commentInfo.content}</Markdown>
          </div>
        </>
      )}
      <div className="flex justify-around items-center md:justify-between md:mx-10">
        {isAuthenticated &&
        (user.username === userInfo.user_name || user.mod_in.includes(threadID) || user.roles.includes("admin")) ? (
          <select
            defaultValue={"more"}
            ref={listRef}
            name="more-options"
            title="More Options"
            id="more-options"
            className="text-sm bg-white md:px-2 md:text-base"
            onChange={(e) => handleSelect(e.target.value)}>
            <option value="more">More</option>
            <option value="share">Share</option>
            {user.username === userInfo.user_name && <option value="edit">Edit</option>}
            <option value="delete">Delete</option>
          </select>
        ) : (
          <div className="flex items-center space-x-1" onClick={() => null}>
            <Svg type="share" className="w-4 h-4" />
            <p className="text-sm cursor-pointer md:text-base">Share</p>
          </div>
        )}
        <div
          className="flex items-center space-x-1"
          onClick={() => {
            isAuthenticated ? setIsReply(!isReply) : alert("You need to be logged in.");
          }}>
          <Svg type="comment" className="w-4 h-4" />
          <p className="text-sm cursor-pointer md:text-base">Reply</p>
        </div>
        <div
          className={`${!commentChildren.length && "invisible"} flex items-center space-x-1`}
          onClick={() => setExpandChildren(!expandChildren)}>
          <Svg type="down-arrow" className={`w-4 h-4 ${expandChildren && "rotate-180"}`} />
          <p className="text-sm cursor-pointer md:text-base">{expandChildren ? "Hide" : "Show"}</p>
        </div>
        <div className="flex items-center space-x-2 text-sm md:text-base">
          <Vote
            {...{
              url: "/api/reactions/comment",
              intitalVote: currentUser?.has_upvoted,
              initialCount: commentInfo.comment_karma,
              contentID: commentInfo.id,
              type: "mobile",
            }}
          />
        </div>
      </div>
      {isReply && (
        <CommentMode
          callBackSubmit={(data) => {
            listRef.current.value = "more";
            addComment(data);
            setIsReply(false);
            setExpandChildren(true);
          }}
          callBackCancel={() => {
            setIsReply(false);
            listRef.current.value = "more";
          }}
          colorSquence={colorSquence}
          user={user}
        />
      )}
      <AnimatePresence mode="wait">
        {expandChildren && (
          <ul className={commentChildren.length > 0 && expandChildren && "border-l-2 " + colorSquence()}>
            {commentChildren.map((child, index) => (
              <Comment
                key={child.comment.comment_info.id}
                {...child}
                commentIndex={index}
                parentDelete={deleteComment}
              />
            ))}
          </ul>
        )}
      </AnimatePresence>
    </motion.li>
  );
}

CommentMode.propTypes = {
  user: PropTypes.object,
  colorSquence: PropTypes.func,
  callBackSubmit: PropTypes.func,
  callBackCancel: PropTypes.func,
  defaultValue: PropTypes.string,
};

export function CommentMode({ user, colorSquence, callBackSubmit, callBackCancel, defaultValue = null }) {
  const { isAuthenticated } = AuthConsumer();
  const [preMD, setPreMD] = useState(false);
  const [content, setContent] = useState(defaultValue || "");
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10, transition: { duration: 0.15 } }}
      transition={{ duration: 0.25 }}
      className={`mr-4 space-y-2 bg-white md:text-base ${
        defaultValue !== null ? "" : `border-l-2 ${colorSquence()} py-3 pl-2 `
      }`}>
      <div className="flex items-center space-x-2 text-sm font-medium">
        <img src={user.avatar || avatar} alt="" className="object-cover w-5 h-5 rounded-full" />
        <Link to={`/u/${user.username}`}>{user.username}</Link>
      </div>
      <form
        method="post"
        className="flex flex-col space-y-2"
        onSubmit={(e) => {
          e.preventDefault();
          if (isAuthenticated) {
            callBackSubmit(content);
          } else {
            alert("You need to be logged in.");
          }
        }}>
        {preMD ? (
          <div className="overflow-auto p-2 max-w-full h-24 rounded-md border prose">
            <Markdown options={{ forceBlock: true }}>
              {content.replace("\n", "<br />\n") || "This is markdown preview"}
            </Markdown>
          </div>
        ) : (
          <textarea
            autoFocus
            defaultValue={content}
            onChange={(e) => setContent(e.target.value)}
            className="p-2 w-full h-24 text-sm rounded-md border md:text-base focus:outline-none"
          />
        )}
        <div className="flex self-end space-x-2">
          <button type="submit" className="px-2 py-1 font-bold text-white bg-blue-600 rounded-md md:px-5">
            Submit
          </button>
          <button
            onClick={() => setPreMD(!preMD)}
            type="button"
            className="px-2 py-1 font-bold text-white bg-green-600 rounded-md md:px-5">
            {preMD ? "Close Preview" : "Preview"}
          </button>
          <button
            onClick={() => callBackCancel()}
            className="px-2 py-1 font-bold text-white bg-red-600 rounded-md md:px-5">
            Cancel
          </button>
        </div>
      </form>
    </motion.div>
  );
}
