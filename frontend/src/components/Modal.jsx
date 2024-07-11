import { motion } from "framer-motion";
import PropTypes from "prop-types";
import { useRef } from "react";
import useEventListener from "../hooks/useEventListener";

Modal.propTypes = {
  children: PropTypes.node,
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
    <motion.div
      initial={{ opacity: 0, background: "rgba(0,0,0,0)" }}
      animate={{ opacity: 1, background: "rgba(0,0,0,0.9)" }}
      transition={{ duration: 0.25 }}
      exit={{ opacity: 0 }}
      ref={ref}
      style={{ margin: 0 }}
      className="flex fixed inset-0 z-20 justify-center items-center min-h-screen min-w-screen">
      {children}
    </motion.div>
  );
}
