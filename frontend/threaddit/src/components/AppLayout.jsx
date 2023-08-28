import { Outlet } from "react-router-dom";
import Navbar from "./Navbar.jsx";
import Svg from "./Svg.jsx";
import { useState } from "react";
import Modal from "./Modal.jsx";
import NewComment from "./NewPost.jsx";
import AuthConsumer from "./AuthContext.jsx";

export function AppLayout() {
  const [showModal, setShowModal] = useState(false);
  const { isAuthenticated } = AuthConsumer();
  return (
    <div className="flex flex-col min-h-screen min-w-screen">
      <Navbar />
      <main className="flex-1 bg-theme-cultured">
        <Outlet />
      </main>
      {isAuthenticated && (
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
