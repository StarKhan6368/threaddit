import Svg from "../../components/Svg.jsx";
import {useEffect, useState} from "react";
import {Form, Link, useActionData, useNavigate} from "react-router-dom";
import AuthConsumer from "../../components/AuthContext.jsx";
import {AppLogo} from "../../components/Navbar.jsx";

export function Login() {
    const [showPass, setShowPass] = useState(false);
    const [clear, setClear] = useState(false);
    const navigate = useNavigate();
    const actionData = useActionData();
    const authData = AuthConsumer();
    useEffect(() => {
        setClear(actionData?.errors === undefined)
    }, [actionData])
    if (authData.isAuthenticated) {
        return navigate("/home")
    }
    if (actionData?.user) {
        authData.login(actionData.user);
        return navigate("/home", {replace: true});
    }
    return (
        <div className="flex justify-center items-center min-h-screen min-w-screen md:space-x-10 bg-theme-cultured">
            <AppLogo forBanner={true} />
            <div className="flex flex-col bg-white space-y-10 p-10 rounded-md">
                <h1 className={`font-semibold text-2xl tracking-wide ${actionData?.errors && !clear && 'font-bold uppercase text-theme-orange'}`}>
                    {actionData?.errors && !clear ? actionData.errors.message : "Welcome to Threaddit!"}
                </h1>
                <Form className="flex flex-col items-center bg-white space-y-5" method="post" action="/login">
                    <label htmlFor="email" className="flex flex-col space-y-1">
                        <span className="pl-2 font-light text-sm">Email</span>
                        <input type="email" name="email" id="email" required onChange={() => setClear(true)}
                               className="border-b pr-24 py-2 focus:outline-none focus:border-black px-2" />
                    </label>
                    <label htmlFor="password" className="flex flex-col space-y-1">
                        <span className="pl-2 font-light text-sm">Password</span>
                        <div className="flex items-center border-b">
                            <input type={`${showPass ? 'text' : 'password'}`} name="password" id="password"
                                   className="pr-20 py-2 focus:outline-none px-2" required minLength={8}/>
                            {showPass ? <Svg type="eye-open" className="w-6 h-6" onClick={() => setShowPass(!showPass)}/>
                                :<Svg type="eye-close" className="w-6 h-6" onClick={() => setShowPass(!showPass)}/>
                            }
                        </div>
                    </label>
                    <button type="submit"
                            className="rounded-md bg-theme-orange py-2 w-full text-white font-semibold active:scale-95">
                        Log in
                    </button>
                </Form>
                <div className="flex justify-between">
                    <Link to="/forgot_password"
                            className="font-semibold group flex hover:text-theme-orange cursor-pointer">
                        Forgot Password
                        <Svg type="arrow-right" className="invisible group-hover:visible w-6 h-6
                            text-theme-orange duration-200 group-hover:translate-x-1"></Svg>
                    </Link>
                    <Link to="/register"
                            className="flex hover:text-theme-orange group font-semibold cursor-pointer">
                        Signup
                        <Svg type="arrow-right" className="invisible group-hover:visible w-6 h-6
                            text-theme-orange duration-200 group-hover:translate-x-1"></Svg>
                    </Link>
                </div>
            </div>
        </div>
    );
}


export async function userLoginAction({request}) {
    const data = Object.fromEntries(await request.formData());
    const response = await fetch("api/user/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({email: data.email, password: data.password})
    })
    if (response.ok) {
        return {user: await response.json()}
    }
    return {errors: await response.json()}
}

export default Login;
