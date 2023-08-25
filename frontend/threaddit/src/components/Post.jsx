import PropTypes from "prop-types";
import Svg from "./Svg";

Post.propTypes = {
  post: PropTypes.object,
};

export function Post({ post }) {
  return (
    <div className="flex flex-col items-center rounded-xl border hover:shadow-sm md:flex-row border-theme-gray-blue p-0.5">
      <div className="flex flex-col flex-1 p-5 space-y-5 h-full md:space-y-0 md:space-x-4 md:flex-row">
        {post.post_info.media && (
          <img
            src={post.post_info.media}
            alt=""
            className="w-full h-full rounded-md duration-500 md:h-28 md:w-28 hover:scale-110"
          />
        )}
        <div className="flex flex-col flex-1 justify-between space-y-3 h-full cursor-pointer">
          <h3 className="text-lg font-semibold text-ellipsis">{post.post_info.title}</h3>
          <div className="flex justify-between">
            <div className="flex items-center text-sm font-medium md:space-x-2">
              <p>Posted by u/{post.user_info.user_name}</p>
              <img src={post.user_info.user_avatar} alt="" className="w-5 h-5 rounded-full" />
              <p>
                in <span>{post.thread_info.thread_name}</span>
              </p>
              <img src={post.thread_info.logo} alt="" className="w-5 h-5 rounded-full" />
            </div>
            <p className="hidden text-sm font-light md:block">{post.post_info.created_at}</p>
          </div>
          <p className="text-sm font-light md:hidden">{post.post_info.created_at}</p>
        </div>
      </div>
      <div className="flex justify-evenly m-5 w-full h-full md:flex-col md:w-fit">
        <div className="flex items-center space-x-2 cursor-pointer group">
          <Svg type="comment" className="w-5 h-5" />
          <div className="flex space-x-1">
            <span>{post.post_info.comments_count}</span>
            <p>Comments</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 cursor-pointer group">
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
        {/* <div className="flex items-center md:hidden"></div> */}
      </div>
      <div className="hidden flex-col justify-around items-center my-3 w-28 h-full border-l md:flex border-theme-gray-blue">
        <div className="px-5 py-1 bg-orange-100 rounded-md">
          <Svg type="down-arrow" className="w-10 h-10 rotate-180" />
        </div>
        <p className="text-lg font-semibold">
          <span>{post.post_info.post_karma}</span>
        </p>
        <div className="px-5 py-1 bg-blue-50 rounded-md group">
          <Svg type="down-arrow" className="w-10 h-10" />
        </div>
      </div>
    </div>
  );
}

export default Post;
