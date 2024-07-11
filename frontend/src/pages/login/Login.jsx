import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthConsumer from "../../components/AuthContext.jsx";
import Loader from "../../components/Loader.jsx";
import { AppLogo } from "../../components/Navbar.jsx";
import Svg from "../../components/Svg.jsx";

export function Login() {
  const [showPass, setShowPass] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { isAuthenticated, login } = AuthConsumer();
  const navigate = useNavigate();
  const { mutate, status, error, reset } = useMutation({
    mutationFn: async () => {
      return await axios.post("https://elegant-manifestation-production.up.railway.app/api/user/login", { email, password }).then((res) => login(res.data));
    },
    onSuccess: () => navigate("/home"),
  });
  useEffect(() => {
    document.title = "Threaddit | Login";
    return () => {
      document.title = "Threaddit";
    }
  })
  if (isAuthenticated) {
    return navigate("/home");
  }
  return (
    <div className="flex justify-center items-center min-h-screen md:space-x-10 bg-theme-cultured">
      <AppLogo forBanner={true} />
      <div className="flex flex-col p-5 py-10 space-y-10 bg-white rounded-md shadow-xl md:p-5">
        <div className="flex justify-center md:hidden">
          <AppLogo>
            <h1 className="font-mono text-3xl font-bold tracking-tight md:block">Threaddit</h1>
          </AppLogo>
        </div>
        <h1
          className={`font-semibold ${status !== "loading" && "text-2xl "} tracking-wide ${error && "font-bold uppercase text-theme-orange"
            }`}>
          {error ? error.response.data.message : status === "loading" ? <Loader forPosts={true} /> : "Welcome Back!"}
        </h1>
        <form
          className="flex flex-col items-center space-y-5 bg-white"
          onSubmit={(e) => {
            e?.preventDefault();
            mutate();
          }}>
          <label htmlFor="email" className="flex flex-col space-y-1">
            <span className="pl-2 text-sm font-light">Email</span>
            <input
              type="email"
              name="email"
              id="email"
              required
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                reset();
              }}
              className="px-2 py-2 pr-24 border-b focus:outline-none focus:border-black"
            />
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
                minLength={8}
                value={password}
                onChange={(event) => {
                  setPassword(event.target.value);
                  reset();
                }}
              />
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
            {status === "loading" ? "Logging in..." : "Log in"}
          </button>
        </form>
        <div className="flex justify-between">
          {/* TODO: Implement forgot password */}
          <Link to="/login" className="flex font-semibold cursor-pointer group hover:text-theme-orange">
            Forgot Password
            <Svg
              type="arrow-right"
              className="invisible w-6 h-6 duration-200 group-hover:visible text-theme-orange group-hover:translate-x-1"></Svg>
          </Link>
          <Link to="/register" className="flex font-semibold cursor-pointer hover:text-theme-orange group">
            Signup
            <Svg
              type="arrow-right"
              className="invisible w-6 h-6 duration-200 group-hover:visible text-theme-orange group-hover:translate-x-1"></Svg>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
