"use client";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

const TOKEN_KEY = "orqestra_auth_token";
const USER_KEY = "orqestra_auth_user";

interface AuthContextValue {
  token: string | null;
  username: string | null;
  login: (username: string, password: string) => Promise<void>;
  signup: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue>({
  token: null,
  username: null,
  login: async () => {},
  signup: async () => {},
  logout: () => {},
  isAuthenticated: false,
});

const API = () => process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    const user = localStorage.getItem(USER_KEY);
    /* eslint-disable react-hooks/set-state-in-effect */
    if (stored && user) {
      setToken(stored);
      setUsername(user);
    }
    setReady(true);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  useEffect(() => {
    if (!ready) return;
    const isPublic = pathname === "/auth/login" || pathname === "/auth/signup";
    if (!token && !isPublic) {
      router.push("/auth/login");
    }
  }, [ready, token, pathname, router]);

  const login = useCallback(async (username: string, password: string) => {
    const res = await fetch(`${API()}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error((body as { detail?: string }).detail || "Login failed");
    }
    const data = (await res.json()) as { token: string; username: string };
    localStorage.setItem(TOKEN_KEY, data.token);
    localStorage.setItem(USER_KEY, data.username);
    setToken(data.token);
    setUsername(data.username);
  }, []);

  const signup = useCallback(async (username: string, password: string) => {
    const res = await fetch(`${API()}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error((body as { detail?: string }).detail || "Signup failed");
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUsername(null);
    router.push("/auth/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        token,
        username,
        login,
        signup,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
