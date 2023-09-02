import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import * as PropType from "prop-types";
import { Link } from "react-router-dom";

export function ThreadsSidebar() {
  const { data } = useQuery({
    queryKey: ["threads/all"],
    queryFn: async () => {
      return await axios.get("/api/threads").then((res) => res.data);
    },
  });
  return (
    <aside className="hidden flex-col w-56 md:flex">
      {data?.subscribed.length !== 0 && (
        <>
          <div className="flex flex-col m-5 space-y-4">
            <div className="flex justify-between w-48 cursor-pointer">
              <h2 className="font-semibold uppercase">Subscribed</h2>
              <span className="pr-1">ALL</span>
            </div>
            <SideBarComponent threadList={data?.subscribed} />
          </div>
          <span className="mx-5 border border-theme-silver-chalice"></span>
        </>
      )}
      <div className="flex flex-col m-5 space-y-4">
        <div className="flex justify-between w-48 cursor-pointer">
          <h2 className="font-semibold uppercase">Top Threads</h2>
          <span className="pr-1">ALL</span>
        </div>
        <SideBarComponent threadList={data?.all} />
      </div>
      <span className="mx-5 border border-theme-silver-chalice"></span>
      <div className="flex flex-col m-5 space-y-4">
        <div className="flex justify-between w-48 cursor-pointer">
          <h2 className="font-semibold uppercase">Popular Threads</h2>
          <span className="pr-1">ALL</span>
        </div>
        <SideBarComponent threadList={data?.popular} />
      </div>
    </aside>
  );
}

SideBarComponent.propTypes = {
  threadList: PropType.array,
};
function SideBarComponent({ threadList }) {
  return (
    <ul className="flex flex-col space-y-4 w-48 list-none">
      {threadList?.slice(0, 10).map((thread) => (
        <Link to={`/${thread.name}`} className="flex justify-between w-48 cursor-pointer" key={thread.name}>
          <div className={`flex items-center space-x-3 ${!thread.logo && "pl-9"}`}>
            {thread.logo && <img src={thread.logo} alt="" className="w-6 h-6 rounded-full" />}
            <span className="">{thread.name}</span>
          </div>
          <span className="p-1 px-2 text-sm font-semibold rounded-md bg-theme-gray-blue">{thread.subscriberCount}</span>
        </Link>
      ))}
    </ul>
  );
}
export default ThreadsSidebar;
