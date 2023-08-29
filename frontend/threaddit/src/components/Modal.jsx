import PropTypes from "prop-types";
import useEventListener from "../hooks/useEventListener";
import { useRef } from "react";

Modal.propTypes = {
  children: PropTypes.node,
  showModal: PropTypes.bool,
  setShowModal: PropTypes.func,
};
export default function Modal({ children, setShowModal }) {
  const ref = useRef();
  useEventListener(
    "click",
    (e) => {
      if (e.target === ref.current) {
        setShowModal(false);
      }
    },
    document
  );
  return (
    <div
      ref={ref}
      style={{ margin: 0 }}
      className="z-20 fixed inset-0 min-h-screen min-w-screen flex justify-center items-center bg-black/[0.7]">
      {children}
    </div>
  );
}
