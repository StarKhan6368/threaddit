import Svg from "../../components/Svg.jsx";
import { useEffect, useState } from "react";
import { Form, Link, useActionData, useNavigate } from "react-router-dom";
import AuthConsumer from "../../components/AuthContext.jsx";
import { AppLogo } from "../../components/Navbar.jsx";

export function Login() {
  const [showPass, setShowPass] = useState(false);
  const [clear, setClear] = useState(false);
  const navigate = useNavigate();
  const actionData = useActionData();
  const authData = AuthConsumer();
  useEffect(() => {
    setClear(actionData?.errors === undefined);
  }, [actionData]);
  if (authData.isAuthenticated) {
    navigate("/home");
  }
  if (actionData?.user) {
    authData.login(actionData.user);
    setTimeout(navigate("/home", { replace: true }), 1000);
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
          className={`font-semibold text-2xl tracking-wide ${
            actionData?.errors && !clear && "font-bold uppercase text-theme-orange"
          }`}>
          {actionData?.errors && !clear ? actionData.errors.message : "Welcome Back!"}
        </h1>
        <Form className="flex flex-col items-center space-y-5 bg-white" method="post" action="/login">
          <label htmlFor="email" className="flex flex-col space-y-1">
            <span className="pl-2 text-sm font-light">Email</span>
            <input
              type="email"
              name="email"
              id="email"
              required
              onChange={() => setClear(true)}
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
            className="py-2 w-full font-semibold text-white rounded-md bg-theme-orange active:scale-95">
            Log in
          </button>
        </Form>
        <div className="flex justify-between">
          <Link to="/forgot_password" className="flex font-semibold cursor-pointer group hover:text-theme-orange">
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

export async function userLoginAction({ request }) {
  const data = Object.fromEntries(await request.formData());
  const response = await fetch("api/user/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email: data.email, password: data.password }),
  });
  if (response.ok) {
    return { user: await response.json() };
  }
  return { errors: await response.json() };
}

export default Login;
