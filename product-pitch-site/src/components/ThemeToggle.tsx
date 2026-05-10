"use client";

import { useState, useEffect } from "react";

/**
 * Item 15: Dark/Light mode toggle.
 * Persists preference in localStorage. Defaults to dark.
 * Uses CSS custom properties for seamless switching.
 */
export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem("kovelai_theme");
    if (saved === "light") {
      setIsDark(false);
      document.documentElement.classList.remove("dark");
      document.documentElement.classList.add("light");
    }
  }, []);

  const toggle = () => {
    const next = !isDark;
    setIsDark(next);
    if (next) {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
      localStorage.setItem("kovelai_theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.classList.add("light");
      localStorage.setItem("kovelai_theme", "light");
    }
  };

  if (!mounted) return null;

  return (
    <button
      onClick={toggle}
      className="fixed bottom-6 right-6 z-[999] w-11 h-11 rounded-full bg-[#161b22]/90 backdrop-blur-md border border-[#30363d] flex items-center justify-center text-lg hover:border-[#00bcd4]/40 hover:shadow-lg hover:shadow-[#00bcd4]/10 transition-all duration-300 group"
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      <span
        className="transition-transform duration-300 group-hover:rotate-45"
        style={{ filter: "none" }}
      >
        {isDark ? "☀️" : "🌙"}
      </span>
    </button>
  );
}
