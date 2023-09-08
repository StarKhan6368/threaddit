import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthConsumer from "../../components/AuthContext.jsx";
import { AppLogo } from "../../components/Navbar.jsx";
import Svg from "../../components/Svg.jsx";
import Loader from "../../components/Loader.jsx";

export function Register() {
  const navigate = useNavigate();
  const { isAuthenticated, login } = AuthConsumer();
  const [showPass, setShowPass] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { mutate, error, status } = useMutation({
    mutationFn: async () => {
      return await axios.post("/api/user/register", { username, email, password }).then((res) => login(res.data));
    },
    onSuccess: () => navigate("/home"),
  });
  if (isAuthenticated) {
    return navigate("/home");
  }
  const {
    username: usernameError,
    email: emailError,
    password: passwordError,
  } = error ? error.response.data.errors : {};
  return (
    <div
      className="flex justify-center items-center w-screen h-screen md:space-x-10 bg-theme-cultured"
      onSubmit={(e) => {
        e.preventDefault();
        mutate();
      }}>
      <AppLogo forBanner={true} />
      <div className="flex flex-col p-5 py-10 space-y-10 bg-white rounded-md shadow-xl md:p-5">
        <div className="flex justify-center md:hidden">
          <AppLogo>
            <h1 className="font-mono text-3xl font-bold tracking-tight md:block">Threaddit</h1>
          </AppLogo>
        </div>
        <h1 className={`${status !== "loading" && "text-2xl"} font-semibold tracking-wide`}>
          {status === "loading" ? <Loader forPosts={true} /> : "Welcome Back!"}
        </h1>
        <form className="flex flex-col items-center space-y-5 bg-white">
          <label htmlFor="email" className="flex flex-col space-y-1">
            <span className="pl-2 text-sm font-light">Username</span>
            <input
              type="text"
              name="username"
              id="username"
              required
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
              }}
              maxLength={15}
              minLength={4}
              className="px-2 py-2 pr-24 border-b focus:outline-none focus:border-black"
            />
            {usernameError?.map((e) => (
              <abbr title={e} className="w-72 text-sm font-semibold no-underline truncate text-theme-orange" key={e}>
                {e}
              </abbr>
            ))}
          </label>
          <label htmlFor="email" className="flex flex-col space-y-1">
            <span className="pl-2 text-sm font-light">Email</span>
            <input
              type="email"
              name="email"
              id="email"
              required
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
              }}
              className="px-2 py-2 pr-24 border-b focus:outline-none focus:border-black"
            />
            {emailError?.map((e) => (
              <aabr title={e} className="w-72 text-sm font-semibold truncate underline-none text-theme-orange" key={e}>
                {e}
              </aabr>
            ))}
          </label>
          <label htmlFor="password" className="flex flex-col space-y-1">
            <span className="pl-2 text-sm font-light">Password</span>
            <div className="flex items-center border-b">
              <input
                type={`${showPass ? "text" : "password"}`}
                name="password"
                id="password"
                className="px-2 py-2 pr-20 focus:outline-none"
                required
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                }}
                minLength={8}
              />
              {passwordError?.map((e) => (
                <aabr
                  title={e}
                  className="w-72 text-sm font-semibold truncate underline-none text-theme-orange"
                  key={e}>
                  {e}
                </aabr>
              ))}
              {showPass ? (
                <Svg type="eye-open" className="w-6 h-6" onClick={() => setShowPass(!showPass)} />
              ) : (
                <Svg type="eye-close" className="w-6 h-6" onClick={() => setShowPass(!showPass)} />
              )}
            </div>
          </label>
          <button
            type="submit"
            disabled={status === "loading"}
            className="py-2 w-full font-semibold text-white rounded-md bg-theme-orange active:scale-95">
            {status === "loading" ? "Signing Up..." : "Sign Up"}
          </button>
        </form>
        <div className="flex justify-between">
          <Link to="/forgot_password" className="flex font-semibold cursor-pointer group hover:text-theme-orange">
            Forgot Password
            <Svg
              type="arrow-right"
              className="invisible w-6 h-6 duration-200 group-hover:visible text-theme-orange group-hover:translate-x-1"></Svg>
          </Link>
          <Link to="/login" className="flex font-semibold cursor-pointer hover:text-theme-orange group">
            Login
            <Svg
              type="arrow-right"
              className="invisible w-6 h-6 duration-200 group-hover:visible text-theme-orange group-hover:translate-x-1"></Svg>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Register;
