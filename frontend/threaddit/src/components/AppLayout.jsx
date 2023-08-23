import {Outlet} from "react-router-dom";
import Navbar from "./Navbar.jsx";

export function AppLayout() {
    return (
        <div className="flex flex-col min-h-screen min-w-screen">
            <Navbar/>
            <main className="bg-theme-cultured flex-1">
                <Outlet/>
            </main>
        </div>
    )
}

export default AppLayout;
