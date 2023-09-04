import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Suspense, lazy } from "react";
import { Navigate, RouterProvider, createBrowserRouter } from "react-router-dom";
import AppLayout from "./components/AppLayout.jsx";
import { AuthProvider } from "./components/AuthContext.jsx";
import Loader from "./components/Loader.jsx";
import RequireAuth from "./components/PrivateRoute.jsx";
import { userLoginAction } from "./pages/login/Login.jsx";
import { userRegisterAction } from "./pages/register/Register.jsx";

const Feed = lazy(() => import("./pages/feed/Feed.jsx"));
const FullPost = lazy(() => import("./pages/fullPost/FullPost.jsx"));
const Inbox = lazy(() => import("./pages/inbox/Inbox.jsx"));
const Login = lazy(() => import("./pages/login/Login.jsx"));
const Profile = lazy(() => import("./pages/profile/Profile.jsx"));
const Register = lazy(() => import("./pages/register/Register.jsx"));
const SavedPosts = lazy(() => import("./pages/saved/SavedPosts.jsx"));
const SubThread = lazy(() => import("./pages/thread/SubThread.jsx"));

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      {
        path: "/",
        element: <Navigate to="/all" />,
      },
      {
        path: "/:feedName",
        element: <Feed />,
      },
      {
        path: "/post/:postId",
        element: <FullPost />,
      },
      {
        path: "/u/:username",
        element: <Profile />,
      },
      {
        path: "/t/:threadName",
        element: <SubThread />,
      },
      {
        path: "/saved",
        element: (
          <RequireAuth>
            <SavedPosts />
          </RequireAuth>
        ),
      },
      {
        path: "/inbox",
        element: (
          <RequireAuth>
            <Inbox />
          </RequireAuth>
        ),
      },
    ],
  },
  {
    path: "/login",
    element: <Login />,
    action: userLoginAction,
  },
  {
    path: "/register",
    element: <Register />,
    action: userRegisterAction,
  },
]);

const queryClient = new QueryClient({});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ReactQueryDevtools initialIsOpen={false} />
      <AuthProvider>
        <Suspense fallback={<Loader />}>
          <RouterProvider router={router} />
        </Suspense>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
