import { useState } from "react";
import { Form, Link, useActionData, useNavigate } from "react-router-dom";
import Svg from "../../components/Svg.jsx";
import AuthConsumer from "../../components/AuthContext.jsx";
import { AppLogo } from "../../components/Navbar.jsx";

export function Register() {
  const actionData = useActionData();
  const navigate = useNavigate();
  const authData = AuthConsumer();
  if (authData.isAuthenticated) {
    navigate("/home");
  }
  console.log(actionData);
  if (actionData?.user) {
    authData.login(actionData.user);
  }
  const [showPass, setShowPass] = useState(false);
  return (
    <div className="flex justify-center items-center w-screen h-screen md:space-x-10 bg-theme-cultured">
      <AppLogo forBanner={true} />
      <div className="flex flex-col p-5 py-10 space-y-10 bg-white rounded-md shadow-xl md:p-5">
        <div className="flex justify-center md:hidden">
          <AppLogo>
            <h1 className="font-mono text-3xl font-bold tracking-tight md:block">Threaddit</h1>
          </AppLogo>
        </div>
        <h1 className="text-2xl font-semibold tracking-wide">Welcome to Threaddit!</h1>
        <Form className="flex flex-col items-center space-y-5 bg-white" method="post" action="/register">
          <label htmlFor="email" className="flex flex-col space-y-1">
            <span className="pl-2 text-sm font-light">Username</span>
            <input
              type="text"
              name="username"
              id="username"
              required
              maxLength={15}
              minLength={4}
              className="px-2 py-2 pr-24 border-b focus:outline-none focus:border-black"
            />
            {actionData?.errors?.username?.map((e) => (
              <aabr title={e} className="w-72 text-sm font-semibold truncate underline-none text-theme-orange" key={e}>
                {e}
              </aabr>
            ))}
          </label>
          <label htmlFor="email" className="flex flex-col space-y-1">
            <span className="pl-2 text-sm font-light">Email</span>
            <input
              type="email"
              name="email"
              id="email"
              required
              className="px-2 py-2 pr-24 border-b focus:outline-none focus:border-black"
            />
            {actionData?.errors?.email?.map((e) => (
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
                minLength={8}
              />
              {actionData?.errors?.password?.map((e) => (
                <span className="text-sm font-semibold text-theme-orange" key={e}>
                  {e}
                </span>
              ))}
              {showPass ? (
                <Svg type="eye-open" className="w-6 h-6" onClick={() => setShowPass(!showPass)} />
              ) : (
                <Svg type="eye-close" className="w-6 h-6" onClick={() => setShowPass(!showPass)} />
              )}
            </div>
          </label>
          <button type="submit" className="py-2 w-full font-semibold text-white rounded-md bg-theme-orange active:scale-95">
            Sign up
          </button>
        </Form>
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

export async function userRegisterAction({ request }) {
  const dataForm = Object.fromEntries(await request.formData());
  const response = await fetch("api/user/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username: dataForm.username, email: dataForm.email, password: dataForm.password }),
  });
  const data = await response.json();
  if (response.status === 201) {
    return { user: data };
  }
  return { errors: data.errors };
}
export default Register;
