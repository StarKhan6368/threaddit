import { useQuery } from "@tanstack/react-query";
import PropTypes from "prop-types";
import { useRef, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import avatar from "../assets/avatar.png";
import axios from "axios"
import threads from "../assets/threads.png";
import AuthConsumer from "../components/AuthContext.jsx";
import Svg from "../components/Svg.jsx";
import useClickOutside from "../hooks/useClickOutside";

export function Navbar() {
  const { isAuthenticated, user, logout } = AuthConsumer();
  return (
    <nav className="flex justify-between items-center mx-3 h-16 md:p-5">
      <AppLogo />
      <div className="flex items-center md:space-x-10">
        <ul
          className={`list-none hidden md:flex space-x-10 text-gray-600 fill-current 
                    ${!isAuthenticated && "flex-1 space-x-20"}`}>
          <NavLink
            to={`${isAuthenticated ? "/home" : "/login"}`}
            className={({ isActive }) =>
              `duration-500 group flex space-x-1 group cursor-pointer ${isActive && "text-theme-red-coral"}`
            }>
            <Svg type="home" className="w-6 h-6" />
            <h2 className="font-semibold group-hover:text-theme-red-coral">Home</h2>
          </NavLink>
          <NavLink
            to="/popular"
            className={({ isActive }) => `group flex space-x-1 group cursor-pointer ${isActive && "text-theme-red-coral"}`}>
            <Svg type="popular" className="w-6 h-6" />
            <h2 className="font-semibold group-hover:text-theme-red-coral">Popular</h2>
          </NavLink>
          <NavLink
            to="/all"
            className={({ isActive }) => `group flex space-x-1 group cursor-pointer ${isActive && "text-theme-red-coral"}`}>
            <Svg type="all" className="w-6 h-6" />
            <h2 className="font-semibold group-hover:text-theme-red-coral">All</h2>
          </NavLink>
        </ul>
        <ThreadSearch />
      </div>
      {isAuthenticated ? (
        <div className="flex items-center md:space-x-6">
          <NavLink to="/inbox" className={({ isActive }) => `${isActive && "text-theme-red-coral"}`}>
            <Svg type="message" className="hidden w-6 h-6 md:block" />
          </NavLink>
          <NavLink to="/notifications" className={({ isActive }) => `${isActive && "text-theme-red-coral"}`}>
            <Svg type="notifications" className="hidden w-6 h-6 md:block" />
          </NavLink>
          <Link to="/profile" className="hidden md:flex items-center space-x-2 bg-theme-cultured rounded-3xl pr-3 py-0.5">
            <img
              src={user.profile ? user.profile : avatar}
              alt="profile-picture"
              className="hidden w-10 h-10 rounded-full duration-500 cursor-pointer hover:scale-125 md:block"
            />
            <div className="hidden text-sm font-semibold md:block">
              <p className="text-gray-700">{user.username}</p>
              <p className="text-gray-500 truncate">karma: {user.karma.user_karma}</p>
            </div>
          </Link>
          <button onClick={logout} className="hidden flex-col items-center md:flex">
            <Svg type="circle-logout" className="hidden w-6 h-6 duration-300 rotate-180 md:block hover:scale-110" />
            <span className="text-sm font-semibold">Logout</span>
          </button>
          <Svg type="down-arrow" className="w-9 h-9 md:w-6 md:h-6 md:hidden" />
        </div>
      ) : (
        <>
          <Link to="/login" className="flex font-semibold cursor-pointer hover:text-theme-orange group">
            Log in
            <Svg
              type="arrow-right"
              className="invisible w-6 h-6 duration-200 group-hover:visible text-theme-orange group-hover:translate-x-1"></Svg>
          </Link>
        </>
      )}
    </nav>
  );
}

AppLogo.propTypes = {
  forBanner: PropTypes.bool,
  children: PropTypes.node,
};
export function AppLogo({ forBanner = false, children }) {
  if (forBanner) {
    return (
      <div className="hidden relative flex-col justify-center items-center space-y-5 rounded-md cursor-pointer md:flex group">
        <img src={threads} alt="threadit-logo" />
        <span
          className="hidden md:block absolute w-4 h-4
                    bg-theme-orange rounded-full bottom-[6rem] z-20 right-[7.9rem] group-hover:animate-bounce"></span>
        <span className="hidden md:block absolute w-4 h-4 bg-theme-cultured rounded-full bottom-[6rem] z-10 right-[7.9rem]"></span>
        <h1 className="font-mono text-6xl font-bold tracking-tight">Threaddit</h1>
        <p className="text-lg font-semibold">The Internet Home Place, where many communities reside</p>
        {children}
      </div>
    );
  }
  return (
    <Link to="/" className="flex relative items-center space-x-3 cursor-pointer group">
      <img src={threads} className="w-10 h-10" alt="threadit-logo" />
      <span
        className="hidden md:block absolute w-2 h-2 bg-theme-red-coral rounded-full
                    right-[1.3rem] top-[0.2rem] z-20 group-hover:animate-bounce"></span>
      <span className="hidden md:block absolute w-2 h-2.5 bg-white rounded-full right-[1.3rem] top-[0.1rem] z-10"></span>
      <h1 className="hidden font-mono text-3xl font-bold tracking-tight md:block">Threaddit</h1>
      {children}
    </Link>
  );
}

function ThreadSearch() {
  const searchRef = useRef();
  const [search, setSearch] = useState("");
  const queryData = useQuery({
    queryKey: ["threads/search", search],
    queryFn: async ({ signal }) => {
      const promise = new Promise((resolve) => setTimeout(resolve, 500)).then(async () => {
        return await axios.get(`/api/threads/search/${search}`, {
          signal,
        }).then((data) => data.data)
      });
      return promise;
    },
    enabled: search.length > 0,
  })
  useClickOutside(searchRef, () => {
    setSearch("");
  });
  return (
    <div className="flex items-center p-2.5 space-x-3 rounded-md bg-neutral-100 relative">
      <Svg type="search" className="w-6 h-6" />
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        type="search"
        name="search"
        id="search"
        className="py-0.5 bg-neutral-100 focus:outline-none md:pr-20"
        placeholder="Find community"
      />
      {queryData?.data && (
        <ul
          className="flex absolute right-0 top-full flex-col p-5 mt-3 space-y-5 w-full list-none bg-white rounded-md border shadow-xl border-y-theme-gray-blue"
          ref={searchRef}>
          {queryData?.data?.slice(0, 5).map((subthread) => (
            <Link to={`/${subthread.name}`} className="flex space-x-5 cursor-pointer" key={subthread.name}>
              <img src={subthread.logo} className="w-10 h-10 rounded-full" />
              <div className="flex flex-col">
                <p className="font-semibold tracking-wide">{subthread.name}</p>
                <span className="text-sm font-light">{subthread.subscriberCount} Members</span>
              </div>
            </Link>
          ))}
          <span className="w-full border border-theme-orange"></span>
          <li className="flex justify-center items-center m-0 font-semibold cursor-pointer group">
            <p>Search For &quot;{search}&quot;</p>
            <Svg type="arrow-right" className="w-6 h-6 duration-500 group-hover:translate-x-1" />
          </li>
        </ul>
      )}
    </div>
  );
}
export default Navbar;
