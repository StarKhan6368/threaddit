import { useQuery } from "@tanstack/react-query";
import PropTypes from "prop-types";
import { useRef, useState } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import avatar from "../assets/avatar.png";
import axios from "axios";
import threads from "../assets/threads.png";
import AuthConsumer from "../components/AuthContext.jsx";
import Svg from "../components/Svg.jsx";
import useClickOutside from "../hooks/useClickOutside";
import Modal from "./Modal";
import { NewThread } from "./NewThread";

export function Navbar() {
  const { isAuthenticated, user, logout } = AuthConsumer();
  const location = useLocation();
  const navigate = useNavigate();
  return (
    <nav className="flex justify-between items-center mx-1 h-16 md:p-5">
      <AppLogo />
      <div className="flex items-center md:space-x-10">
        <div
          className={`list-none hidden md:flex space-x-10 text-gray-600 fill-current 
                    ${!isAuthenticated && "flex-1 space-x-20"}`}>
          <NavLink
            to={`${isAuthenticated ? "/home" : "/login"}`}
            className={({ isActive }) =>
              `duration-500 group flex space-x-1 group cursor-pointer ${isActive && "text-theme-orange"}`
            }>
            <Svg type="home" className="w-6 h-6" />
            <h2 className="font-semibold group-hover:text-theme-orange">Home</h2>
          </NavLink>
          <NavLink
            to="/popular"
            className={({ isActive }) =>
              `group flex space-x-1 group cursor-pointer ${isActive && "text-theme-orange"}`
            }>
            <Svg type="popular" className="w-6 h-6" />
            <h2 className="font-semibold group-hover:text-theme-orange">Popular</h2>
          </NavLink>
          <NavLink
            to="/all"
            className={({ isActive }) =>
              `group flex space-x-1 group cursor-pointer ${isActive && "text-theme-orange"}`
            }>
            <Svg type="all" className="w-6 h-6" />
            <h2 className="font-semibold group-hover:text-theme-orange">All</h2>
          </NavLink>
        </div>
        <ThreadSearch callBackFunc={(threadUrl) => navigate(threadUrl)} />
      </div>
      <div className="flex items-center md:space-x-6">
        {isAuthenticated && (
          <>
            <NavLink to="/saved" className={({ isActive }) => `${isActive && "text-theme-orange"}`} title="saved">
              <Svg type="save" className="hidden w-6 h-6 md:block" />
            </NavLink>
            <NavLink to="/inbox" className={({ isActive }) => `${isActive && "text-theme-orange"}`} title="inbox">
              <Svg type="message" className="hidden w-6 h-6 md:block" />
            </NavLink>
            <Link
              to={`/u/${user.username}`}
              className="hidden md:flex items-center space-x-2 bg-theme-cultured rounded-3xl pr-3 py-0.5">
              <img loading="lazy" width="auto" height="100%"
                src={user.avatar || avatar}
                className="object-cover w-10 h-10 rounded-full duration-500 cursor-pointer hover:scale-125 md:block"
              />
              <div className="text-sm font-semibold md:block">
                <p className="text-gray-700">{user.username}</p>
                <p className="text-gray-500 truncate">karma: {user.karma.user_karma}</p>
              </div>
            </Link>
            <button onClick={logout} className="hidden flex-col items-center md:flex">
              <Svg type="circle-logout" className="w-6 h-6 duration-300 rotate-180 md:block hover:scale-110" />
              <span className="text-sm font-semibold">Logout</span>
            </button>
          </>
        )}
        <select
          name="page"
          id="page"
          className="px-1 py-3 mr-1 text-center rounded-md md:hidden bg-theme-cultured"
          onChange={(e) => {
            if (e.target.value !== "logout") {
              navigate(e.target.value);
            } else {
              logout();
              return navigate("/all");
            }
          }}
          value={location.pathname}>
          <optgroup label="Feeds">
            {isAuthenticated && <option value="/home">Home</option>}
            <option value="/popular">Popular</option>
            <option value="/all">All</option>
          </optgroup>
          <optgroup label="Other">
            {isAuthenticated ? (
              <>
                <option value="/inbox">Inbox</option>
                <option value="/saved">Saved</option>
                <option value={`/u/${user.username}`}>Profile</option>
                <option value="logout">Logout</option>
              </>
            ) : (
              <>
                <option value="/register">Register</option>
                <option value="/login">Login</option>
              </>
            )}
          </optgroup>
        </select>
      </div>
      {!isAuthenticated && (
        <Link to="/login" className="hidden font-semibold cursor-pointer md:flex hover:text-theme-orange group">
          Login
          <Svg
            type="arrow-right"
            className="invisible w-6 h-6 duration-200 group-hover:visible text-theme-orange group-hover:translate-x-1"></Svg>
        </Link>
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
        <img src={threads} alt="threadit-logo" className="object-cover" />
        <span
          className="hidden md:block absolute w-4 h-4
                    bg-theme-orange rounded-full bottom-[5.9rem] z-20 right-[8rem] group-hover:animate-bounce"></span>
        <span className="hidden md:block absolute w-4 h-4 bg-theme-cultured rounded-full bottom-[5.9rem] z-10 right-[8rem]"></span>
        <h1 className="font-mono text-6xl font-bold tracking-tight">Threaddit</h1>
        <p className="text-lg font-semibold">The Internet Home Place, where many communities reside</p>
        {children}
      </div>
    );
  }
  return (
    <Link to="/" className="flex relative items-center space-x-3 cursor-pointer group">
      <img src={threads} className="object-cover w-10 h-10" alt="threadit-logo" />
      <span
        className="hidden md:block absolute w-2 h-2 bg-theme-orange rounded-full
                    right-[1.4rem] top-[0.2rem] z-20 group-hover:animate-bounce"></span>
      <span className="hidden md:block absolute w-2 h-2 bg-white rounded-full right-[1.4rem] top-[0.2rem] z-10"></span>
      <h1 className="hidden font-mono text-3xl font-bold tracking-tight md:block">Threaddit</h1>
      {children}
    </Link>
  );
}

ThreadSearch.propTypes = {
  callBackFunc: PropTypes.func,
  forPost: PropTypes.bool,
};
export function ThreadSearch({ callBackFunc, forPost = false }) {
  const [showModal, setShowModal] = useState(false);
  const searchRef = useRef();
  const [search, setSearch] = useState("");
  const queryData = useQuery({
    queryKey: ["threads/search", search],
    queryFn: async ({ signal }) => {
      const promise = new Promise((resolve) => setTimeout(resolve, 500)).then(async () => {
        return await axios
          .get(`/api/threads/search`, {
            params: { name: search },
            signal,
          })
          .then((data) => data.data);
      });
      return promise;
    },
    enabled: search.length > 0 && search.replace(/\s/g, "").length > 0,
  });
  useClickOutside(searchRef, () => {
    setSearch("");
  });
  const threadNames = queryData.data ? queryData.data.map((thread) => thread.name) : [];
  return (
    <div
      className="flex items-center py-2.5 pl-2 md:p-2.5 space-x-3 rounded-md bg-neutral-100 relative"
      ref={searchRef}>
      <Svg type="search" className="w-6 h-6" />
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        type="search"
        name="search"
        id="search"
        className="py-0.5 w-48  md:w-full bg-neutral-100 focus:outline-none md:pr-20"
        placeholder="Find community"
      />
      {queryData.data && search && (
        <ul className="flex absolute right-0 top-full z-50 flex-col p-5 mt-3 space-y-5 w-full list-none bg-white rounded-md border shadow-xl border-y-theme-gray-blue">
          {queryData.data.slice(0, 5).map((subthread) => (
            <li
              className={`flex space-x-5 cursor-pointer ${!subthread.logo && "pl-[3.75rem]"}`}
              key={subthread.name}
              onClick={() => {
                callBackFunc(forPost ? { id: subthread.id, name: subthread.name } : subthread.name);
                setSearch("");
              }}>
              {subthread.logo && <img src={subthread.logo} className="object-cover w-10 h-10 rounded-full" />}
              <div className="flex flex-col">
                <p className="text-sm font-semibold tracking-wide md:text-base">{subthread.name}</p>
                <span className="text-xs font-light md:text-sm">{subthread.subscriberCount} Members</span>
              </div>
            </li>
          ))}
          {!threadNames.includes(`t/${search}`) && !forPost && (
            <>
              <span className="w-full border border-theme-orange"></span>
              <div
                className="flex justify-center items-center m-0 font-semibold cursor-pointer group"
                onClick={() => {
                  setShowModal(true);
                  setSearch("");
                }}>
                <p className="text-sm md:text-base">Create subthread &quot;{search}&quot;</p>
                <Svg type="arrow-right" className="w-6 h-6 duration-500 group-hover:translate-x-1" />
              </div>
            </>
          )}
        </ul>
      )}
      {showModal && (
        <Modal setShowModal={setShowModal} showModal={showModal}>
          <NewThread subThreadName={search} setShowModal={setShowModal} />
        </Modal>
      )}
    </div>
  );
}
export default Navbar;
