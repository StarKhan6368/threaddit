import { createContext, useContext, useState } from "react";
import PropTypes from "prop-types";

const AuthContext = createContext(null);

AuthProvider.propTypes = {
  children: PropTypes.any,
};

export function AuthProvider({ children }) {
  const localData = JSON.parse(localStorage.getItem("user"));
  const [isAuthenticated, setIsAuthenticated] = useState(!!localData);
  const [user, setUser] = useState(localData || {});
  function login(userInfo) {
    localStorage.setItem("user", JSON.stringify(userInfo));
    setUser(userInfo);
    setIsAuthenticated(true);
  }
  function logout() {
    fetch("api/user/logout").then(() => {
      localStorage.removeItem("user");
      setUser({});
      setIsAuthenticated(false);
    });
  }
  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, user }}>
      {children}
    </AuthContext.Provider>
  );
}

export default function AuthConsumer() {
  return useContext(AuthContext);
}
