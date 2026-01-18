/**
 * Responsive Hook - Detects screen breakpoints
 * @module hooks/useResponsive
 */

import { useState, useEffect, useCallback } from 'react';

export type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface ResponsiveState {
    breakpoint: Breakpoint;
    isMobile: boolean;
    isTablet: boolean;
    isDesktop: boolean;
    width: number;
    height: number;
}

const BREAKPOINTS = {
    xs: 0,
    sm: 480,
    md: 640,
    lg: 768,
    xl: 1024,
} as const;

function getBreakpoint(width: number): Breakpoint {
    if (width < BREAKPOINTS.sm) return 'xs';
    if (width < BREAKPOINTS.md) return 'sm';
    if (width < BREAKPOINTS.lg) return 'md';
    if (width < BREAKPOINTS.xl) return 'lg';
    return 'xl';
}

export function useResponsive(): ResponsiveState {
    const [state, setState] = useState<ResponsiveState>(() => {
        const width = typeof window !== 'undefined' ? window.innerWidth : 1024;
        const height = typeof window !== 'undefined' ? window.innerHeight : 768;
        const breakpoint = getBreakpoint(width);

        return {
            breakpoint,
            isMobile: breakpoint === 'xs' || breakpoint === 'sm',
            isTablet: breakpoint === 'md' || breakpoint === 'lg',
            isDesktop: breakpoint === 'xl',
            width,
            height,
        };
    });

    const handleResize = useCallback(() => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        const breakpoint = getBreakpoint(width);

        setState({
            breakpoint,
            isMobile: breakpoint === 'xs' || breakpoint === 'sm',
            isTablet: breakpoint === 'md' || breakpoint === 'lg',
            isDesktop: breakpoint === 'xl',
            width,
            height,
        });
    }, []);

    useEffect(() => {
        // Initial call
        handleResize();

        // Debounced resize handler
        let timeoutId: ReturnType<typeof setTimeout>;
        const debouncedResize = () => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(handleResize, 100);
        };

        window.addEventListener('resize', debouncedResize);
        window.addEventListener('orientationchange', handleResize);

        return () => {
            window.removeEventListener('resize', debouncedResize);
            window.removeEventListener('orientationchange', handleResize);
            clearTimeout(timeoutId);
        };
    }, [handleResize]);

    return state;
}

// Hook to detect touch capability
export function useTouch(): boolean {
    const [isTouch, setIsTouch] = useState(false);

    useEffect(() => {
        setIsTouch(
            'ontouchstart' in window ||
            navigator.maxTouchPoints > 0
        );
    }, []);

    return isTouch;
}

// Hook to detect safe areas (for notched devices)
export function useSafeArea() {
    const [safeArea, setSafeArea] = useState({
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
    });

    useEffect(() => {
        const computeStyles = () => {
            const style = getComputedStyle(document.documentElement);
            setSafeArea({
                top: parseInt(style.getPropertyValue('--sat') || '0', 10),
                bottom: parseInt(style.getPropertyValue('--sab') || '0', 10),
                left: parseInt(style.getPropertyValue('--sal') || '0', 10),
                right: parseInt(style.getPropertyValue('--sar') || '0', 10),
            });
        };

        // Set CSS variables for safe areas
        document.documentElement.style.setProperty('--sat', 'env(safe-area-inset-top)');
        document.documentElement.style.setProperty('--sab', 'env(safe-area-inset-bottom)');
        document.documentElement.style.setProperty('--sal', 'env(safe-area-inset-left)');
        document.documentElement.style.setProperty('--sar', 'env(safe-area-inset-right)');

        computeStyles();
        window.addEventListener('resize', computeStyles);
        return () => window.removeEventListener('resize', computeStyles);
    }, []);

    return safeArea;
}
