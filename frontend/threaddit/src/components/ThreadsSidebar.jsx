import {useQuery} from "@tanstack/react-query";
import * as PropType from "prop-types";

export function ThreadsSidebar() {
    const {all, subscribed, popular} = useQuery({
        queryKey: ["subthreads/all"],
        queryFn: async () => {
            return await fetch("/api/subthreads/all").then(res => res.json())
        }
    })
    console.log(all)
    return (
        <aside className="md:flex flex-col w-56 hidden">
            <div className="flex flex-col m-5 space-y-4">
                <div className="flex justify-between w-48 cursor-pointer">
                    <h2 className="uppercase font-semibold">Favourites</h2>
                    <span className="pr-1">ALL</span>
                </div>
                <ul className="list-none flex flex-col w-48 space-y-4">
                    <li className="flex justify-between w-48 cursor-pointer">
                        <div className="flex items-center space-x-3">
                            <img src="avatar.png" alt="" className="rounded-full h-6 w-6" />
                                <span className="">r/funny</span>
                        </div>
                        <span className="bg-theme-gray-blue rounded-md text-sm p-1 px-2 font-semibold">100</span>
                    </li>
                </ul>
            </div>
            <span className="border border-theme-silver-chalice mx-5"></span>
            <div className="flex flex-col m-5 space-y-4">
                <div className="flex justify-between w-48 cursor-pointer">
                    <h2 className="uppercase font-semibold">Favourites</h2>
                    <span className="pr-1">ALL</span>
                </div>
                <ul className="list-none flex flex-col w-48 space-y-4">
                    <li className="flex justify-between w-48 cursor-pointer">
                        <div className="flex items-center space-x-3">
                            <img src="avatar.png" alt="" className="rounded-full h-6 w-6" />
                                <span className="">r/funny</span>
                        </div>
                        <span className="bg-theme-gray-blue rounded-md text-sm p-1 px-2 font-semibold">100</span>
                    </li>
                </ul>
            </div>
            <span className="border border-theme-silver-chalice mx-5"></span>
            <div className="flex flex-col m-5 space-y-4">
                <div className="flex justify-between w-48 cursor-pointer">
                    <h2 className="uppercase font-semibold">Favourites</h2>
                    <span className="pr-1">ALL</span>
                </div>
                <ul className="list-none flex flex-col w-48 space-y-4">
                    <li className="flex justify-between w-48 cursor-pointer">
                        <div className="flex items-center space-x-3">
                            <img src="avatar.png" alt="" className="rounded-full h-6 w-6" />
                                <span className="">r/funny</span>
                        </div>
                        <span className="bg-theme-gray-blue rounded-md text-sm p-1 px-2 font-semibold">100</span>
                    </li>
                </ul>
            </div>
        </aside>
    )
}


sideBarComponent.propTypes = {
    logo: PropType.string,
    name: PropType.string,
    subscribers: PropType.number
}
function sideBarComponent({logo, name, subscribers}) {
    return (
        <ul className="list-none flex flex-col w-48 space-y-4">
            <li className="flex justify-between w-48 cursor-pointer">
                <div className="flex items-center space-x-3">
                    <img src={logo} alt="" className="rounded-full h-6 w-6" />
                        <span className="">{name}</span>
                </div>
                <span className="bg-theme-gray-blue rounded-md text-sm p-1 px-2 font-semibold">{subscribers}</span>
            </li>
        </ul>
    )
}
export default ThreadsSidebar;
