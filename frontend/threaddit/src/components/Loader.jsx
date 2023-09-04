import "./loader.css";

export function Loader() {
  return (
    <div className="flex justify-center items-center w-screen h-screen">
      <div style={{ color: "#FF4500" }} className="la-pacman la-dark la-3x">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    </div>
  );
}

export default Loader;
