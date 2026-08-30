import { createContext, useContext, useState, useCallback } from "react";
import {
  loginUser,
  registerUser,
  setSession,
  clearSession,
  getStoredUser,
  getToken,
} from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser());
  const [token, setToken] = useState(getToken());

  const login = useCallback(async (username, password) => {
    const data = await loginUser(username, password);
    setSession(data.access_token, data.user);
    setUser(data.user);
    setToken(data.access_token);
    return data.user;
  }, []);

  const register = useCallback(async (username, password, role) => {
    return registerUser(username, password, role);
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, token, isAuthenticated: Boolean(token), login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
