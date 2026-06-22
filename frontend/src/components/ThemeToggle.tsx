"use client";
import { useCallback, useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

function getTheme(): "light" | "dark" {
  if (typeof document === "undefined") return "dark";
  return document.documentElement.getAttribute("data-theme") === "light"
    ? "light"
    : "dark";
}

function setTheme(theme: "light" | "dark") {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem("orqestra-theme", theme);
  } catch {}
}

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const [theme, setThemeState] = useState<"light" | "dark">("dark");

  useEffect(() => {
    setMounted(true);
    setThemeState(getTheme());
  }, []);

  useEffect(() => {
    if (!mounted) return;
    const handler = () => setThemeState(getTheme());
    window.addEventListener("themechange", handler);
    return () => window.removeEventListener("themechange", handler);
  }, [mounted]);

  const toggle = useCallback(() => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    setThemeState(next);
  }, [theme]);

  return (
    <button
      onClick={toggle}
      className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-surface-3 transition-all duration-200 border border-transparent hover:border-border"
      title={mounted ? `Switch to ${theme === "light" ? "dark" : "light"} theme` : ""}
    >
      {mounted ? (
        theme === "light" ? <Moon size={16} /> : <Sun size={16} />
      ) : (
        <div className="w-4 h-4" />
      )}
      <span>{mounted ? (theme === "light" ? "Dark Mode" : "Light Mode") : "\u00A0"}</span>
    </button>
  );
}
