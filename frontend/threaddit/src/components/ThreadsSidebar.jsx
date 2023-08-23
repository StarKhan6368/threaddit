import { useQuery } from "@tanstack/react-query";
import * as PropType from "prop-types";

export function ThreadsSidebar() {
  const { all, subscribed, popular } = useQuery({
    queryKey: ["subthreads/all"],
    queryFn: async () => {
      return await fetch("/api/subthreads/all").then((res) => res.json());
    },
  });
  console.log(all);
  return (
    <aside className="flex-col hidden w-56 md:flex">
      <div className="flex flex-col m-5 space-y-4">
        <div className="flex justify-between w-48 cursor-pointer">
          <h2 className="font-semibold uppercase">Favourites</h2>
          <span className="pr-1">ALL</span>
        </div>
        <ul className="flex flex-col w-48 space-y-4 list-none">
          <li className="flex justify-between w-48 cursor-pointer">
            <div className="flex items-center space-x-3">
              <img src="avatar.png" alt="" className="w-6 h-6 rounded-full" />
              <span className="">r/funny</span>
            </div>
            <span className="p-1 px-2 text-sm font-semibold rounded-md bg-theme-gray-blue">
              100
            </span>
          </li>
        </ul>
      </div>
      <span className="mx-5 border border-theme-silver-chalice"></span>
      <div className="flex flex-col m-5 space-y-4">
        <div className="flex justify-between w-48 cursor-pointer">
          <h2 className="font-semibold uppercase">Favourites</h2>
          <span className="pr-1">ALL</span>
        </div>
        <ul className="flex flex-col w-48 space-y-4 list-none">
          <li className="flex justify-between w-48 cursor-pointer">
            <div className="flex items-center space-x-3">
              <img src="avatar.png" alt="" className="w-6 h-6 rounded-full" />
              <span className="">r/funny</span>
            </div>
            <span className="p-1 px-2 text-sm font-semibold rounded-md bg-theme-gray-blue">
              100
            </span>
          </li>
        </ul>
      </div>
      <span className="mx-5 border border-theme-silver-chalice"></span>
      <div className="flex flex-col m-5 space-y-4">
        <div className="flex justify-between w-48 cursor-pointer">
          <h2 className="font-semibold uppercase">Favourites</h2>
          <span className="pr-1">ALL</span>
        </div>
        <ul className="flex flex-col w-48 space-y-4 list-none">
          <li className="flex justify-between w-48 cursor-pointer">
            <div className="flex items-center space-x-3">
              <img src="avatar.png" alt="" className="w-6 h-6 rounded-full" />
              <span className="">r/funny</span>
            </div>
            <span className="p-1 px-2 text-sm font-semibold rounded-md bg-theme-gray-blue">
              100
            </span>
          </li>
        </ul>
      </div>
    </aside>
  );
}

sideBarComponent.propTypes = {
  logo: PropType.string,
  name: PropType.string,
  subscribers: PropType.number,
};
function sideBarComponent({ logo, name, subscribers }) {
  return (
    <ul className="flex flex-col w-48 space-y-4 list-none">
      <li className="flex justify-between w-48 cursor-pointer">
        <div className="flex items-center space-x-3">
          <img src={logo} alt="" className="w-6 h-6 rounded-full" />
          <span className="">{name}</span>
        </div>
        <span className="p-1 px-2 text-sm font-semibold rounded-md bg-theme-gray-blue">
          {subscribers}
        </span>
      </li>
    </ul>
  );
}
export default ThreadsSidebar;
