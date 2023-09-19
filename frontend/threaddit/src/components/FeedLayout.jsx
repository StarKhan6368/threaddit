import { Outlet } from "react-router-dom";
import ThreadsSidebar from "./ThreadsSidebar";

export default function FeedLayout() {
  return (
    <div className="flex flex-1 max-w-full bg-theme-cultured">
      <ThreadsSidebar />
      <Outlet />
    </div>
  );
}
