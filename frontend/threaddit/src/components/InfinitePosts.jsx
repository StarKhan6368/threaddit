import { useInfiniteQuery } from "@tanstack/react-query";
import axios from "axios";
import { AnimatePresence } from "framer-motion";
import PropTypes from "prop-types";
import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import Post from "./Post";
import Loader from "./Loader";

InfinitePostsLayout.propTypes = {
  linkUrl: PropTypes.string,
  apiQueryKey: PropTypes.string,
  forSaved: PropTypes.bool,
  enabled: PropTypes.bool,
};

export default function InfinitePostsLayout({ linkUrl, apiQueryKey, forSaved = false, enabled = true }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const sortBy = searchParams.get("sortBy") || "top";
  const duration = searchParams.get("duration") || "alltime";
  const { data, isFetching, hasNextPage, fetchNextPage } = useInfiniteQuery({
    queryKey: ["posts", apiQueryKey, sortBy, duration],
    queryFn: async ({ pageParam = 0 }) => {
      return await axios
        .get(`/api/${linkUrl}?limit=${20}&offset=${pageParam * 20}&sortby=${sortBy}&duration=${duration}`)
        .then((data) => data.data);
    },
    enabled: enabled,
    getNextPageParam: (lastPage, pages) => {
      if (lastPage.length < 20) return undefined;
      return pages.length;
    },
  });
  useEffect(() => {
    const onScroll = (event) => {
      const { scrollTop, scrollHeight, clientHeight } = event.target.scrollingElement;
      if (scrollHeight - scrollTop <= clientHeight * 2 && hasNextPage && !isFetching) {
        fetchNextPage();
      }
    };
    window.addEventListener("scroll", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
    };
  }, [fetchNextPage, isFetching, hasNextPage]);
  function handleDurationChange(newDuration) {
    searchParams.set("duration", newDuration);
    setSearchParams(searchParams);
  }
  function handleSortByChange(newSortBy) {
    searchParams.set("sortBy", newSortBy);
    setSearchParams(searchParams);
  }
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
              onChange={(e) => handleSortByChange(e.target.value)}
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
              onChange={(e) => handleDurationChange(e.target.value)}
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
              onClick={() => handleDurationChange("day")}>
              Today
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                duration === "week" && "bg-theme-gray-blue"
              }`}
              onClick={() => handleDurationChange("week")}>
              Week
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                duration === "month" && "bg-theme-gray-blue"
              }`}
              onClick={() => handleDurationChange("month")}>
              Month
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                duration === "alltime" && "bg-theme-gray-blue"
              }`}
              onClick={() => handleDurationChange("alltime")}>
              All
            </li>
          </ul>
          <ul className="hidden mr-5 space-x-5 list-none md:flex">
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                sortBy === "hot" && "bg-theme-gray-blue"
              }`}
              onClick={() => handleSortByChange("hot")}>
              Hot
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                sortBy === "new" && "bg-theme-gray-blue"
              }`}
              onClick={() => handleSortByChange("new")}>
              New
            </li>
            <li
              className={`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${
                sortBy === "top" && "bg-theme-gray-blue"
              }`}
              onClick={() => handleSortByChange("top")}>
              Top
            </li>
          </ul>
        </header>
      )}
      {isFetching && <Loader forPosts={true} />}
      <div className="flex flex-col flex-1 space-y-2 w-full h-full md:space-y-3">
        {data?.pages.map((pageData, index) => (
          <ul className="flex flex-col flex-1 space-y-2 w-full h-full md:space-y-3" key={index}>
            <AnimatePresence initial={index == 0}>
              {pageData?.map((post, index) => (
                <Post post={post} key={post.post_info.id} postIndex={index} />
              ))}
            </AnimatePresence>
          </ul>
        ))}
      </div>
    </div>
  );
}
