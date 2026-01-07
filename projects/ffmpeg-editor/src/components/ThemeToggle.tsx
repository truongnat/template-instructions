import { motion } from "framer-motion";
import { Sun, Moon } from "lucide-react";
import { useTheme } from "@/hooks/useTheme";
import { Button } from "@/components/ui/button";
import { themeIconVariants } from "@/lib/animations";

/**
 * Animated theme toggle button with sun/moon icon rotation
 * Provides smooth transition between light and dark modes
 */
export function ThemeToggle() {
    const { toggleTheme, isDark } = useTheme();

    return (
        <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="relative overflow-hidden"
            animate={false}
        >
            <motion.span
                className="absolute inset-0 flex items-center justify-center"
                variants={themeIconVariants}
                initial={false}
                animate={isDark ? "dark" : "light"}
            >
                {isDark ? (
                    <Moon className="h-4 w-4" />
                ) : (
                    <Sun className="h-4 w-4" />
                )}
            </motion.span>
            <span className="sr-only">Toggle theme</span>
        </Button>
    );
}
