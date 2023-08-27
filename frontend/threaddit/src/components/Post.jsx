import PropTypes from "prop-types";
import { Link, useNavigate } from "react-router-dom";
import Svg from "./Svg";
import Vote from "./Vote";

Post.propTypes = {
  post: PropTypes.object,
};

export function Post({ post }) {
  const navigate = useNavigate();
  return (
    <div className="flex bg-white flex-col items-center rounded-xl border-2 hover:shadow-sm md:flex-row border-theme-gray-blue p-1">
      <div
        onClick={() => navigate(`/post/${post.post_info.id}`)}
        className="h-full flex flex-col flex-1 w-full p-3 space-y-5 md:space-y-0 md:space-x-4 md:flex-row">
        {post.post_info.media && (
          <img
            src={post.post_info.media}
            alt=""
            className="w-full h-full rounded-md duration-500 md:h-32 md:w-32 hover:scale-110"
          />
        )}
        <div className="flex flex-col flex-1 justify-between space-y-3 cursor-pointer">
          <h3 className="text-lg font-semibold text-ellipsis">{post.post_info.title}</h3>
          <div className="flex justify-between">
            <div className="flex items-center text-sm font-medium md:space-x-2">
              <Link to={`/u/${post.user_info.user_name}`}>Posted by u/{post.user_info.user_name}</Link>
              <img src={post.user_info.user_avatar} alt="" className="w-5 h-5 rounded-full" />
              <p>
                in <Link to={`/${post.thread_info.thread_name}`}>{post.thread_info.thread_name}</Link>
              </p>
              <img src={post.thread_info.logo} alt="" className="w-5 h-5 rounded-full" />
            </div>
            <p className="hidden text-sm font-light md:block">{post.post_info.created_at}</p>
          </div>
          <p className="text-sm font-light md:hidden">{post.post_info.created_at}</p>
        </div>
      </div>
      <div className="flex justify-evenly md:mx-5 w-full h-full md:flex-col md:w-fit">
        <Link to={`/post/${post.post_info.id}`} className="flex items-center space-x-2 cursor-pointer group">
          <Svg type="comment" className="w-5 h-5" />
          <div className="flex space-x-1">
            <span>{post.post_info.comments_count}</span>
            <p>Comments</p>
          </div>
        </Link>
        <div className="hidden md:flex items-center space-x-2 cursor-pointer group">
          <Svg type="share" className="w-5 h-5" />
          <div className="flex space-x-1">
            <span></span>
            <p>Share</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 cursor-pointer group">
          <Svg className="w-5 h-5" type="more" />
          <div className="flex space-x-1">
            <p>More</p>
          </div>
        </div>
        <div className="flex items-center md:hidden space-x-3">
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
    </div>
  );
}

export default Post;
