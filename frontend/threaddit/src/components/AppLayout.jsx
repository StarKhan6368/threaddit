import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import AuthConsumer from "./AuthContext.jsx";
import Modal from "./Modal.jsx";
import Navbar from "./Navbar.jsx";
import NewComment from "./NewPost.jsx";
import Svg from "./Svg.jsx";

export function AppLayout() {
  const [showModal, setShowModal] = useState(false);
  const { isAuthenticated } = AuthConsumer();
  const location = useLocation();
  return (
    <div className="flex flex-col min-h-screen min-w-screen">
      <Navbar />
      <main className="flex flex-col flex-1 bg-theme-cultured">
        <Outlet />
      </main>
      {isAuthenticated && location.pathname != "/inbox" && (
        <div
          className="fixed right-5 bottom-5 w-14 h-14 rounded-xl bg-theme-orange active:scale-90"
          onClick={() => setShowModal(true)}>
          <Svg
            type="add"
            className="text-white cursor-pointer fill-current hover:text-white"
            onClick={() => setShowModal(true)}
          />
        </div>
      )}
      {showModal && isAuthenticated && (
        <Modal showModal={showModal} setShowModal={setShowModal}>
          <NewComment setShowModal={setShowModal} />
        </Modal>
      )}
    </div>
  );
}

export default AppLayout;
