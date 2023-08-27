import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { timeAgo } from "../pages/fullPost/utils";
import Svg from "./Svg";
import Vote from "./Vote";

Comment.propTypes = {
  children: PropTypes.array,
  comment: PropTypes.object,
};

export default function Comment({ children, comment }) {
  const timePassed = timeAgo(new Date(comment.comment_info.created_at));
  if (children.length > 0) {
    {
      return (
        <div className="border-l-2 rounded-t-lg space-y-2">
          <Comment key={comment.comment_info.id} {...{ children: [], comment }} />
          <ul className="ml-2 space-y-2">
            {children.map((child) => (
              <Comment key={child.comment.comment_info.id} {...child} />
            ))}
          </ul>
        </div>
      );
    }
  } else {
    return (
      <div className="bg-white w-full p-2 space-y-2 border-2 rounded-xl">
        <div className="flex items-center text-sm font-medium md:space-x-2">
          <img src={comment.user_info.user_avatar} alt="" className="w-5 h-5 rounded-full" />
          <Link to={`/u/${comment.user_info.user_name}`}>{comment.user_info.user_name}</Link>
          <p>{timePassed}</p>
        </div>
        <p className="">{comment.comment_info.content}</p>
        <div className="flex items-center space-x-10 justify-between md:justify-start">
          <div className="flex space-x-2 items-center">
            <Vote
              {...{
                url: "/api/reactions/comment",
                intitalVote: comment.current_user.has_upvoted,
                initialCount: comment.comment_info.comment_karma,
                contentID: comment.comment_info.id,
                type: "mobile",
              }}
            />
          </div>
          <div className="flex items-center space-x-1">
            <Svg type="comment" className="w-5 h-5" />
            <p>Reply</p>
          </div>
          <div className="flex items-center space-x-1">
            <Svg type="share" className="w-5 h-5" />
            <p>Share</p>
          </div>
        </div>
      </div>
    );
  }
}
