import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import PropTypes from "prop-types";
import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext();

AuthProvider.propTypes = {
  children: PropTypes.any,
};

export function AuthProvider({ children }) {
  const localData = JSON.parse(localStorage.getItem("user"));
  const [isAuthenticated, setIsAuthenticated] = useState(!!localData);
  const [user, setUser] = useState(localData || {});
  const { refetch } = useQuery({
    queryKey: ["user"],
    queryFn: async () => {
      return await axios.get("/api/user").then((res) => res.data);
    },
    retry: 1,
    onSuccess: (data) => {
      login(data);
    },
    onError: () => {
      setUser({});
      setIsAuthenticated(false);
    },
    enabled: isAuthenticated,
  });
  useEffect(() => {
    refetch();
    return;
  }, [refetch]);
  function login(userInfo) {
    localStorage.setItem("user", JSON.stringify(userInfo));
    setUser(userInfo);
    setIsAuthenticated(true);
  }
  function logout() {
    axios.get("api/user/logout").then(() => {
      localStorage.removeItem("user");
      setUser({});
      setIsAuthenticated(false);
    });
  }
  return <AuthContext.Provider value={{ isAuthenticated, login, logout, user }}>{children}</AuthContext.Provider>;
}

export default function AuthConsumer() {
  return useContext(AuthContext);
}
