import { useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import PropTypes from "prop-types";
import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext();

AuthProvider.propTypes = {
  children: PropTypes.any,
};

export function AuthProvider({ children }) {
  const queryClient = useQueryClient();
  const localData = JSON.parse(localStorage.getItem("user"));
  const [isAuthenticated, setIsAuthenticated] = useState(!!localData);
  const [user, setUser] = useState(localData || {});
  const { refetch } = useQuery({
    queryKey: ["user"],
    queryFn: async () => {
      return await axios
        .get("/api/user")
        .then((res) => {
          localStorage.setItem("user", JSON.stringify(res.data));
          setUser(res.data);
          setIsAuthenticated(true);
          return res.data;
        })
        .catch(() => {
          setIsAuthenticated(false);
          setUser({});
          return {};
        });
    },
    retry: 1,
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
    queryClient.invalidateQueries();
  }
  function logout() {
    axios.get("api/user/logout").then(() => {
      localStorage.removeItem("user");
      queryClient.invalidateQueries();
      window.location.href = "/all";
    });
  }
  return <AuthContext.Provider value={{ isAuthenticated, login, logout, user }}>{children}</AuthContext.Provider>;
}

export default function AuthConsumer() {
  return useContext(AuthContext);
}
