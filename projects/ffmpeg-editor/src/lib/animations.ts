import { Variants } from "framer-motion";

/**
 * Zoom-like animation variants for smooth UI transitions
 * Optimized for 60fps GPU-accelerated animations
 */

// Modal/Dialog entrance animation (Zoom-style)
export const modalVariants: Variants = {
    hidden: {
        opacity: 0,
        scale: 0.95,
        y: 10,
    },
    visible: {
        opacity: 1,
        scale: 1,
        y: 0,
        transition: {
            type: "spring",
            damping: 25,
            stiffness: 300,
            duration: 0.2,
        },
    },
    exit: {
        opacity: 0,
        scale: 0.95,
        y: 10,
        transition: {
            duration: 0.15,
            ease: "easeOut",
        },
    },
};

// Overlay/backdrop fade animation
export const overlayVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { duration: 0.2 },
    },
    exit: {
        opacity: 0,
        transition: { duration: 0.15 },
    },
};

// Panel slide-in animation (for sidebars, drawers)
export const panelSlideVariants: Variants = {
    hidden: {
        x: -20,
        opacity: 0,
    },
    visible: {
        x: 0,
        opacity: 1,
        transition: {
            type: "spring",
            damping: 20,
            stiffness: 250,
        },
    },
    exit: {
        x: -20,
        opacity: 0,
        transition: {
            duration: 0.15,
        },
    },
};

// Button hover/tap animation
export const buttonVariants: Variants = {
    idle: { scale: 1 },
    hover: {
        scale: 1.02,
        transition: {
            type: "spring",
            stiffness: 400,
            damping: 10,
        },
    },
    tap: { scale: 0.98 },
};

// List item stagger animation
export const listContainerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.05,
            delayChildren: 0.1,
        },
    },
};

export const listItemVariants: Variants = {
    hidden: {
        opacity: 0,
        y: 10,
    },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            type: "spring",
            damping: 20,
            stiffness: 300,
        },
    },
};

// Tooltip/popover animation
export const tooltipVariants: Variants = {
    hidden: {
        opacity: 0,
        scale: 0.96,
        y: 4,
    },
    visible: {
        opacity: 1,
        scale: 1,
        y: 0,
        transition: {
            type: "spring",
            damping: 20,
            stiffness: 300,
        },
    },
};

// Progress bar animation
export const progressVariants: Variants = {
    initial: { scaleX: 0, originX: 0 },
    animate: (progress: number) => ({
        scaleX: progress,
        transition: {
            type: "spring",
            damping: 30,
            stiffness: 200,
        },
    }),
};

// Theme toggle icon rotation
export const themeIconVariants: Variants = {
    light: {
        rotate: 0,
        scale: 1,
        transition: {
            type: "spring",
            stiffness: 200,
            damping: 10,
        },
    },
    dark: {
        rotate: 360,
        scale: 1,
        transition: {
            type: "spring",
            stiffness: 200,
            damping: 10,
        },
    },
};

// Card hover effect
export const cardHoverVariants: Variants = {
    idle: {
        y: 0,
        boxShadow: "0 0 0 rgba(0, 0, 0, 0)",
    },
    hover: {
        y: -2,
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.2)",
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 20,
        },
    },
};

// Fade in/out for general use
export const fadeVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { duration: 0.2 },
    },
    exit: {
        opacity: 0,
        transition: { duration: 0.15 },
    },
};

// Dropdown menu animation
export const dropdownVariants: Variants = {
    hidden: {
        opacity: 0,
        scale: 0.95,
        y: -5,
    },
    visible: {
        opacity: 1,
        scale: 1,
        y: 0,
        transition: {
            type: "spring",
            damping: 20,
            stiffness: 300,
        },
    },
    exit: {
        opacity: 0,
        scale: 0.95,
        y: -5,
        transition: {
            duration: 0.1,
        },
    },
};

// Slider thumb animation
export const sliderThumbVariants: Variants = {
    idle: { scale: 1 },
    hover: {
        scale: 1.2,
        transition: {
            type: "spring",
            stiffness: 400,
            damping: 10,
        },
    },
    drag: {
        scale: 1.3,
        transition: {
            type: "spring",
            stiffness: 400,
            damping: 10,
        },
    },
};

// Timeline playhead animation
export const playheadVariants: Variants = {
    idle: {
        scaleY: 1,
    },
    playing: {
        scaleY: [1, 1.1, 1],
        transition: {
            repeat: Infinity,
            duration: 0.5,
        },
    },
};

// Spring transition presets
export const springTransition = {
    fast: { type: "spring", stiffness: 400, damping: 30 },
    medium: { type: "spring", stiffness: 300, damping: 25 },
    slow: { type: "spring", stiffness: 200, damping: 20 },
    bouncy: { type: "spring", stiffness: 500, damping: 15 },
} as const;

// Ease presets for non-spring animations
export const easePresets = {
    smooth: [0.4, 0, 0.2, 1],
    easeOut: [0, 0, 0.2, 1],
    easeIn: [0.4, 0, 1, 1],
    sharp: [0.4, 0, 0.6, 1],
} as const;
