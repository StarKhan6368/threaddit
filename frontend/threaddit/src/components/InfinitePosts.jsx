import PropTypes from "prop-types";
import Post from "./Post";
import { useEffect } from "react";

InfinitePostsLayout.propTypes = {
  data: PropTypes.object,
  fetchNextpage: PropTypes.func,
  hasNextPage: PropTypes.bool,
  isFetching: PropTypes.bool,
  setSortBy: PropTypes.func,
  setDuration: PropTypes.func,
  sortBy: PropTypes.string,
  duration: PropTypes.string,
  forSaved: PropTypes.bool,
};

export default function InfinitePostsLayout({
  duration,
  hasNextPage,
  isFetching,
  fetchNextpage,
  sortBy,
  setSortBy,
  setDuration,
  forSaved = false,
  data,
}) {
  useEffect(() => {
    const onScroll = (event) => {
      const { scrollTop, scrollHeight, clientHeight } = event.target.scrollingElement;
      if (scrollHeight - scrollTop <= clientHeight * 2 && hasNextPage && !isFetching) {
        fetchNextpage();
      }
    };
    window.addEventListener("scroll", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
    };
  }, [fetchNextpage, hasNextPage, isFetching]);
  return (
    <div
      id="main-content"
      className="flex flex-col flex-1 p-2 space-y-3 w-full h-full rounded-lg m-0.5 bg-theme-cultured md:bg-white md:m-3">
      {!forSaved && (
        <header className="flex justify-between items-center w-full">
          <div className="flex items-center space-x-2 md:hidden">
            <span>Sort by</span>
            <select
              name="sort"
              id="sort"
              className="p-2 px-4 bg-white rounded-md md:bg-theme-cultured"
              onChange={(e) => setSortBy(e.target.value)}
              value={sortBy}>
              <option value="top">Top</option>
              <option value="hot">Hot</option>
              <option value="new">New</option>
            </select>
          </div>
          <div className="flex items-center space-x-2 md:hidden">
            <span>Of</span>
            <select
              name="duration"
              id="duration"
              className="p-2 px-4 bg-white rounded-md md:bg-theme-cultured"
              onChange={(e) => setDuration(e.target.value)}
              value={duration}>
              <option value="day">Day</option>
              <option value="week">Week</option>
              <option value="month">Month</option>
              <option value="year">Year</option>
              <option value="alltime">All Time</option>
            </select>
          </div>
          <ul className="hidden space-x-2 list-none md:flex">
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                duration === "day" && "bg-theme-gray-blue"
              }`}
              onClick={() => setDuration("day")}>
              Today
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                duration === "week" && "bg-theme-gray-blue"
              }`}
              onClick={() => setDuration("week")}>
              Week
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                duration === "month" && "bg-theme-gray-blue"
              }`}
              onClick={() => setDuration("month")}>
              Month
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                duration === "alltime" && "bg-theme-gray-blue"
              }`}
              onClick={() => setDuration("alltime")}>
              All
            </li>
          </ul>
          <ul className="hidden mr-5 space-x-5 list-none md:flex">
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                sortBy === "hot" && "bg-theme-gray-blue"
              }`}
              onClick={() => setSortBy("hot")}>
              Hot
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                sortBy === "new" && "bg-theme-gray-blue"
              }`}
              onClick={() => setSortBy("new")}>
              New
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                sortBy === "top" && "bg-theme-gray-blue"
              }`}
              onClick={() => setSortBy("top")}>
              Top
            </li>
          </ul>
        </header>
      )}
      <div className="flex flex-col flex-1 space-y-2 w-full h-full md:space-y-3">
        {data?.pages.map((pageData, index) => (
          <ul className="flex flex-col flex-1 space-y-2 w-full h-full md:space-y-3" key={index}>
            {pageData?.map((post) => (
              <Post post={post} key={post.post_info.id} />
            ))}
          </ul>
        ))}
      </div>
    </div>
  );
}
