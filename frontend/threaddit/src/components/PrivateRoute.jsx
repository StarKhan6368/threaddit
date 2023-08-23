import { Navigate } from "react-router-dom";
import AuthConsumer from "./AuthContext.jsx";
import PropTypes from "prop-types";

RequireAuth.propTypes = {
  children: PropTypes.node,
  redirectTo: PropTypes.string,
};

function RequireAuth({ children, redirectTo = "/login" }) {
  const { isAuthenticated } = AuthConsumer();
  return isAuthenticated ? (
    children
  ) : (
    <Navigate replace={true} to={redirectTo} />
  );
}

export default RequireAuth;
