import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Suspense, lazy } from "react";
import { Navigate, RouterProvider, createBrowserRouter } from "react-router-dom";
import AppLayout from "./components/AppLayout.jsx";
import { AuthProvider } from "./components/AuthContext.jsx";
import Error from "./components/Error.jsx";
import FeedLayout from "./components/FeedLayout.jsx";
import Loader from "./components/Loader.jsx";
import RequireAuth from "./components/PrivateRoute.jsx";
import Login from "./pages/login/Login.jsx";
import Register from "./pages/register/Register.jsx";

const Feed = lazy(() => import("./pages/feed/Feed.jsx"));
const Profile = lazy(() => import("./pages/profile/Profile.jsx"));
const FullPost = lazy(() => import("./pages/fullPost/FullPost.jsx"));
const Inbox = lazy(() => import("./pages/inbox/Inbox.jsx"));
const SavedPosts = lazy(() => import("./pages/saved/SavedPosts.jsx"));
const SubThread = lazy(() => import("./pages/thread/SubThread.jsx"));

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    errorElement: <Error />,
    children: [
      {
        path: "/",
        element: <FeedLayout />,
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
        ],
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
  },
  {
    path: "/register",
    element: <Register />,
  },
]);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 120000,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Suspense fallback={<Loader />}>
          <RouterProvider router={router} fallbackElement={<Loader />} />
        </Suspense>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
