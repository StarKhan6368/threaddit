import {createBrowserRouter, RouterProvider} from "react-router-dom";
import AppLayout from "./components/AppLayout.jsx";
import HomePage from "./pages/home/HomePage.jsx";
import Popular from "./pages/popular/Popular.jsx";
import All from "./pages/all/All.jsx";
import Inbox from "./pages/inbox/Inbox.jsx";
import Profile from "./pages/profile/Profile.jsx";
import Notifications from "./pages/notifications/Notifications.jsx";
import Login, {userLoginAction} from "./pages/login/Login.jsx";
import Register, {userRegisterAction} from "./pages/register/Register.jsx";
import RequireAuth from "./components/PrivateRoute.jsx";
import {AuthProvider} from "./components/AuthContext.jsx";
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {ReactQueryDevtools} from "@tanstack/react-query-devtools";

const router = createBrowserRouter([
    {
        path: "/",
        element: <AppLayout />,
        children: [
            {
                path: "/",
                element: <All/>
            },
            {
                path: "/popular",
                element: <Popular/>
            },
            {
                path: "/home",
                element: <RequireAuth><HomePage/></RequireAuth>
            },
            {
                path: "/inbox",
                element: <RequireAuth><Inbox/></RequireAuth>
            },
            {
                path: "/notifications",
                element: <RequireAuth><Notifications/></RequireAuth>
            },
            {
                path: "/profile",
                element: <RequireAuth><Profile/></RequireAuth>
            }
        ]
    },
    {
        path: "/login",
        element: <Login/>,
        action: userLoginAction
    },
    {
        path: "/register",
        element: <Register/>,
        action: userRegisterAction
    }
])

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 60 * 1000
        }
    }
});

export function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <ReactQueryDevtools initialIsOpen={false}/>
            <AuthProvider>
                    <RouterProvider router={router}/>
            </AuthProvider>
        </QueryClientProvider>
    )
}

export default App;
