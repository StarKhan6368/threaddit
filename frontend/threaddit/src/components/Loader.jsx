import "./loader.css";
import PropTypes from "prop-types";

Loader.propTypes = {
  forPosts: PropTypes.bool,
  children: PropTypes.node,
};

export function Loader({ forPosts = false, children = null }) {
  return (
    <>
      <div className={`flex justify-center items-center ${forPosts ? "max-w-full max-h-full" : "w-screen h-screen"}`}>
        <div style={{ color: "#FF4500" }} className="la-pacman la-dark la-3x">
          <div></div>
          <div></div>
          <div></div>
          <div></div>
          <div></div>
          <div></div>
        </div>
      </div>
      {children}
    </>
  );
}

export default Loader;
