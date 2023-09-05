import Loader from "./Loader";
import PropTypes from "prop-types";

Error.propTypes = {
  message: PropTypes.string,
  fullScreen: PropTypes.bool,
};

export default function Error({ message = "Something went wrong", fullScreen = true }) {
  return (
    <div
      className={`flex flex-col justify-center items-center space-y-10 ${
        fullScreen ? "w-screen h-screen" : "w-full h-full"
      } bg-theme-cultured`}>
      <Loader forPosts={fullScreen}>
        <h1 className="text-2xl font-bold">{message}</h1>
      </Loader>
    </div>
  );
}
