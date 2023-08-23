import Svg from "../components/Svg.jsx";
import threads from "../assets/threads.png"
import avatar from "../assets/avatar.png"
import {Link, NavLink} from "react-router-dom";
import PropTypes from "prop-types";
import AuthConsumer from "../components/AuthContext.jsx";

export function Navbar() {
    const {isAuthenticated, user, logout} = AuthConsumer();
    return (
        <nav className="flex items-center h-16 md:p-5 mx-3 justify-between">
            <AppLogo/>
            <div className="items-center flex md:space-x-10">
                <ul className={`list-none hidden md:flex space-x-10 text-gray-600 fill-current 
                    ${!isAuthenticated && 'flex-1 space-x-20'}`}>
                    <NavLink to="/home"
                             className={({isActive}) =>
                                 `duration-500 group flex space-x-1 group cursor-pointer ${isActive && 'text-theme-red-coral'}`}>
                        <Svg type="home" className="h-6 w-6"/>
                        <h2 className="font-semibold group-hover:text-theme-red-coral">Home</h2>
                    </NavLink>
                    <NavLink to="/popular"
                             className={({isActive}) =>
                                 `group flex space-x-1 group cursor-pointer ${isActive && 'text-theme-red-coral'}`}>
                        <Svg type="popular" className="h-6 w-6" />
                        <h2 className="font-semibold group-hover:text-theme-red-coral">Popular</h2>
                    </NavLink>
                    <NavLink to="/"
                             className={({isActive}) =>
                                 `group flex space-x-1 group cursor-pointer ${isActive && 'text-theme-red-coral'}`}>
                        <Svg type="all" className="h-6 w-6" />
                        <h2 className="font-semibold group-hover:text-theme-red-coral">All</h2>
                    </NavLink>
                </ul>
                <div className="flex items-center rounded-md bg-neutral-100 p-2.5 space-x-2">
                    <Svg type="search" className="w-6 h-6"/>
                    <input type="search" name="search" id="search"
                           className="bg-neutral-100 focus:outline-none md:pr-20 pr-14"
                           placeholder="Find community or post" />
                </div>
            </div>
            { isAuthenticated ?
                <div className="flex items-center md:space-x-6">
                    <NavLink to="/inbox" className={({isActive}) => `${isActive && 'text-theme-red-coral'}`}>
                        <Svg type="message" className="w-6 h-6 hidden md:block"/>
                    </NavLink>
                    <NavLink to="/notifications" className={({isActive}) => `${isActive && 'text-theme-red-coral'}`}>
                        <Svg type="notifications" className="w-6 h-6 hidden md:block"/>
                    </NavLink>
                    <Link to="/profile" className="hidden md:flex items-center space-x-2 bg-theme-cultured rounded-3xl pr-3 py-0.5">
                        <img src={user.profile ? user.profile : avatar} alt="profile-picture"
                            className="rounded-full h-10 w-10 hover:scale-125 duration-500 cursor-pointer hidden md:block" />
                        <div className="hidden md:block text-sm font-semibold">
                            <p className="text-gray-700">{user.username}</p>
                            <p className="text-gray-500 truncate">{user.roles.map(r => r)}</p>
                        </div>
                    </Link>
                    <button onClick={logout} className="hidden md:flex flex-col items-center">
                        <Svg type="circle-logout" className="w-6 h-6 rotate-180 hidden md:block
                            hover:scale-110 duration-300"/>
                        <span className="text-sm font-semibold">Logout</span>
                    </button>
                    <Svg type="down-arrow" className="md:w-6 md:h-6 md:hidden w-9 h-9"/>
                </div>
                :
                <>
                    <Link to="/login"
                            className="flex hover:text-theme-orange group font-semibold cursor-pointer">
                        Log in
                        <Svg type="arrow-right" className="invisible group-hover:visible w-6 h-6
                            text-theme-orange duration-200 group-hover:translate-x-1"></Svg>
                    </Link>
                </>
            }
        </nav>
    )
}


AppLogo.propTypes = {
    forBanner: PropTypes.bool
}
export function AppLogo({forBanner = false}) {
    if (forBanner) {
        return (
            <div
                className="hidden md:flex flex-col items-center relative group cursor-pointer justify-center space-y-5 rounded-md group">
                <img src={threads} alt="threadit-logo" />
                <span
                    className="hidden md:block absolute w-4 h-4
                    bg-theme-orange rounded-full bottom-[5.6rem] z-20 right-[8.5rem] group-hover:animate-bounce">
                </span>
                <span
                    className="hidden md:block absolute w-4 h-4 bg-white rounded-full bottom-[5.6rem] z-10 right-[8.5rem]"></span>
                <h1 className="font-bold tracking-tight text-6xl font-mono">Threaddit</h1>
                <p className="font-semibold text-lg">The Internet Home Place, where many communities reside</p>
            </div>
        );
    }
    return (
        <Link to="/" className="flex items-center space-x-3 relative group cursor-pointer group">
            <img src={threads} className="w-10 h-10" alt="threadit-logo" />
            <span
                className="hidden md:block absolute w-2 h-2 bg-theme-red-coral rounded-full
                    right-[1.2rem] top-[0.2rem] z-20 group-hover:animate-bounce">
            </span>
            <span
                className="hidden md:block absolute w-2 h-2.5 bg-white rounded-full right-[1.2rem] top-[0.25rem] z-10"></span>
                <h1 className="hidden md:block font-bold text-3xl tracking-tight font-mono">Threaddit</h1>
        </Link>
    )
}
export default Navbar;
