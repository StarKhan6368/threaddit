import {useState} from "react";
import {Form, Link, useActionData, useNavigate} from "react-router-dom";
import Svg from "../../components/Svg.jsx";
import AuthConsumer from "../../components/AuthContext.jsx";
import {AppLogo} from "../../components/Navbar.jsx";

export function Register() {
    const actionData = useActionData();
    const navigate = useNavigate();
    const authData = AuthConsumer();
    if (authData.isAuthenticated) {
        navigate("/home")
    }
    console.log(actionData)
    if (actionData?.user) {
        authData.login(actionData.user);
    }
    const [showPass, setShowPass] = useState(false);
    return (
        <div className="flex justify-center items-center min-h-screen min-w-screen md:space-x-10 bg-theme-cultured">
            <AppLogo forBanner={true} />
            <div className="flex flex-col bg-white space-y-10 p-10 rounded-md">
                <h1 className="font-semibold text-2xl tracking-wide">
                    Welcome to Threaddit!
                </h1>
                <Form className="flex flex-col items-center bg-white space-y-5" method="post" action="/register">
                    <label htmlFor="email" className="flex flex-col space-y-1">
                        <span className="pl-2 font-light text-sm">Username</span>
                        <input type="text" name="username" id="username" required maxLength={15} minLength={4}
                               className="border-b pr-24 py-2 focus:outline-none focus:border-black px-2" />
                        {actionData?.errors?.username?.map(e =>
                            <aabr title={e} className="underline-none text-theme-orange text-sm font-semibold w-72 truncate" key={e}>{e}</aabr>
                        )}
                    </label>
                    <label htmlFor="email" className="flex flex-col space-y-1">
                        <span className="pl-2 font-light text-sm">Email</span>
                        <input type="email" name="email" id="email" required
                               className="border-b pr-24 py-2 focus:outline-none focus:border-black px-2" />
                        {actionData?.errors?.email?.map(e =>
                            <aabr title={e} className="underline-none text-theme-orange text-sm font-semibold w-72 truncate" key={e}>{e}</aabr>
                        )}
                    </label>
                    <label htmlFor="password" className="flex flex-col space-y-1">
                        <span className="pl-2 font-light text-sm">Password</span>
                        <div className="flex items-center border-b">
                            <input type={`${showPass ? 'text' : 'password'}`} name="password" id="password"
                                   className="pr-20 py-2 focus:outline-none px-2" required minLength={8}/>
                            {actionData?.errors?.password?.map(e =>
                                <span className="text-theme-orange text-sm font-semibold" key={e}>{e}</span>
                            )}
                            {showPass ? <Svg type="eye-open" className="w-6 h-6" onClick={() => setShowPass(!showPass)}/>
                                :<Svg type="eye-close" className="w-6 h-6" onClick={() => setShowPass(!showPass)}/>
                            }
                        </div>
                    </label>
                    <button type="submit"
                            className="rounded-md bg-theme-orange py-2 w-full text-white font-semibold active:scale-95">
                        Sign up
                    </button>
                </Form>
                <div className="flex justify-between">
                    <Link to="/forgot_password"
                            className="font-semibold group flex hover:text-theme-orange cursor-pointer">
                        Forgot Password
                        <Svg type="arrow-right" className="invisible group-hover:visible w-6 h-6
                            text-theme-orange duration-200 group-hover:translate-x-1"></Svg>
                    </Link>
                    <Link to="/login"
                            className="flex hover:text-theme-orange group font-semibold cursor-pointer">
                        Login
                        <Svg type="arrow-right" className="invisible group-hover:visible w-6 h-6
                            text-theme-orange duration-200 group-hover:translate-x-1"></Svg>
                    </Link>
                </div>
            </div>
        </div>
    );
}


export async function userRegisterAction({request}) {
    const dataForm = Object.fromEntries(await request.formData());
    const response = await fetch("api/user/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({username: dataForm.username, email: dataForm.email, password: dataForm.password})
    })
    const data = await response.json()
    if (response.status === 201) {
        return {"user": data}
    }
    return {errors: data.errors};
}
export default Register;
