import { useEffect, useCallback } from 'react';

export interface KeyboardShortcuts {
    onPlayPause?: () => void;
    onFrameBack?: () => void;
    onFrameForward?: () => void;
    onSetIn?: () => void;
    onSetOut?: () => void;
    onExport?: () => void;
    onUndo?: () => void;
    onRedo?: () => void;
    onOpenFile?: () => void;
    onEscape?: () => void;
}

export interface ShortcutDefinition {
    key: string;
    ctrl?: boolean;
    shift?: boolean;
    alt?: boolean;
    description: string;
    action: keyof KeyboardShortcuts;
}

export const SHORTCUT_DEFINITIONS: ShortcutDefinition[] = [
    { key: ' ', description: 'Play / Pause', action: 'onPlayPause' },
    { key: 'ArrowLeft', description: 'Step back 1 frame', action: 'onFrameBack' },
    { key: 'ArrowRight', description: 'Step forward 1 frame', action: 'onFrameForward' },
    { key: 'i', description: 'Set In point (trim start)', action: 'onSetIn' },
    { key: 'o', description: 'Set Out point (trim end)', action: 'onSetOut' },
    { key: 's', ctrl: true, description: 'Export', action: 'onExport' },
    { key: 'z', ctrl: true, description: 'Undo', action: 'onUndo' },
    { key: 'z', ctrl: true, shift: true, description: 'Redo', action: 'onRedo' },
    { key: 'y', ctrl: true, description: 'Redo', action: 'onRedo' },
    { key: 'o', ctrl: true, description: 'Open file', action: 'onOpenFile' },
    { key: 'Escape', description: 'Close dialog / Cancel', action: 'onEscape' },
];

export function useKeyboardShortcuts(shortcuts: KeyboardShortcuts, enabled: boolean = true) {
    const handleKeyDown = useCallback((event: KeyboardEvent) => {
        if (!enabled) return;

        // Ignore if typing in an input field
        const target = event.target as HTMLElement;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
            return;
        }

        const { key, ctrlKey, shiftKey, altKey } = event;

        // Find matching shortcut
        const matchedShortcut = SHORTCUT_DEFINITIONS.find(def => {
            const keyMatch = def.key.toLowerCase() === key.toLowerCase();
            const ctrlMatch = !!def.ctrl === ctrlKey;
            const shiftMatch = !!def.shift === shiftKey;
            const altMatch = !!def.alt === altKey;
            return keyMatch && ctrlMatch && shiftMatch && altMatch;
        });

        if (matchedShortcut) {
            const handler = shortcuts[matchedShortcut.action];
            if (handler) {
                event.preventDefault();
                handler();
            }
        }
    }, [shortcuts, enabled]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);
}

// Helper to format shortcut for display
export function formatShortcut(def: ShortcutDefinition): string {
    const parts: string[] = [];
    if (def.ctrl) parts.push('Ctrl');
    if (def.shift) parts.push('Shift');
    if (def.alt) parts.push('Alt');

    let keyDisplay = def.key;
    if (def.key === ' ') keyDisplay = 'Space';
    else if (def.key === 'ArrowLeft') keyDisplay = '←';
    else if (def.key === 'ArrowRight') keyDisplay = '→';
    else if (def.key === 'ArrowUp') keyDisplay = '↑';
    else if (def.key === 'ArrowDown') keyDisplay = '↓';
    else keyDisplay = def.key.toUpperCase();

    parts.push(keyDisplay);
    return parts.join(' + ');
}
