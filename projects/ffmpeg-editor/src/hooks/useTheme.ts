import { useState, useEffect, useCallback } from "react";

type Theme = "dark" | "light" | "system";

/**
 * Hook for managing theme state with localStorage persistence
 * and system preference detection
 */
export function useTheme() {
    const [theme, setThemeState] = useState<Theme>(() => {
        if (typeof window === "undefined") return "dark";

        const stored = localStorage.getItem("theme") as Theme | null;
        if (stored) return stored;

        return window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light";
    });

    const [resolvedTheme, setResolvedTheme] = useState<"dark" | "light">(() => {
        if (typeof window === "undefined") return "dark";

        const stored = localStorage.getItem("theme") as Theme | null;
        if (stored && stored !== "system") return stored;

        return window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light";
    });

    // Apply theme class to document
    useEffect(() => {
        const root = window.document.documentElement;

        let effectiveTheme: "dark" | "light";

        if (theme === "system") {
            effectiveTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
                ? "dark"
                : "light";
        } else {
            effectiveTheme = theme;
        }

        root.classList.remove("light", "dark");
        root.classList.add(effectiveTheme);
        setResolvedTheme(effectiveTheme);
    }, [theme]);

    // Listen for system theme changes
    useEffect(() => {
        if (theme !== "system") return;

        const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

        const handleChange = (e: MediaQueryListEvent) => {
            const newTheme = e.matches ? "dark" : "light";
            const root = window.document.documentElement;
            root.classList.remove("light", "dark");
            root.classList.add(newTheme);
            setResolvedTheme(newTheme);
        };

        mediaQuery.addEventListener("change", handleChange);
        return () => mediaQuery.removeEventListener("change", handleChange);
    }, [theme]);

    const setTheme = useCallback((newTheme: Theme) => {
        localStorage.setItem("theme", newTheme);
        setThemeState(newTheme);
    }, []);

    const toggleTheme = useCallback(() => {
        setTheme(resolvedTheme === "dark" ? "light" : "dark");
    }, [resolvedTheme, setTheme]);

    return {
        theme,
        setTheme,
        toggleTheme,
        resolvedTheme,
        isDark: resolvedTheme === "dark",
    };
}
