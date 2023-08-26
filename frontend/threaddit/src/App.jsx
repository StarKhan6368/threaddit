import { createBrowserRouter, RouterProvider, Navigate } from "react-router-dom";
import AppLayout from "./components/AppLayout.jsx";
import Feed from "./pages/feed/Feed.jsx";
import Inbox from "./pages/inbox/Inbox.jsx";
import Profile from "./pages/profile/Profile.jsx";
import Notifications from "./pages/notifications/Notifications.jsx";
import SubThread from "./pages/thread/SubThread.jsx";
import Login, { userLoginAction } from "./pages/login/Login.jsx";
import Register, { userRegisterAction } from "./pages/register/Register.jsx";
import RequireAuth from "./components/PrivateRoute.jsx";
import { AuthProvider } from "./components/AuthContext.jsx";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

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
        path: "/t/:threadName",
        element: <SubThread />,
      },
      {
        path: "/inbox",
        element: (
          <RequireAuth>
            <Inbox />
          </RequireAuth>
        ),
      },
      {
        path: "/notifications",
        element: (
          <RequireAuth>
            <Notifications />
          </RequireAuth>
        ),
      },
      {
        path: "/profile",
        element: (
          <RequireAuth>
            <Profile />
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

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 5,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ReactQueryDevtools initialIsOpen={false} />
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
