import { useState, useCallback } from 'react';

export interface HistoryState<T> {
    past: T[];
    present: T;
    future: T[];
}

export interface UseHistoryReturn<T> {
    state: T;
    set: (newState: T) => void;
    undo: () => void;
    redo: () => void;
    canUndo: boolean;
    canRedo: boolean;
    clear: () => void;
}

export function useHistory<T>(initialState: T, maxHistory: number = 50): UseHistoryReturn<T> {
    const [history, setHistory] = useState<HistoryState<T>>({
        past: [],
        present: initialState,
        future: []
    });

    const set = useCallback((newState: T) => {
        setHistory(prev => ({
            past: [...prev.past, prev.present].slice(-maxHistory),
            present: newState,
            future: []
        }));
    }, [maxHistory]);

    const undo = useCallback(() => {
        setHistory(prev => {
            if (prev.past.length === 0) return prev;
            const previous = prev.past[prev.past.length - 1];
            const newPast = prev.past.slice(0, -1);
            return {
                past: newPast,
                present: previous,
                future: [prev.present, ...prev.future]
            };
        });
    }, []);

    const redo = useCallback(() => {
        setHistory(prev => {
            if (prev.future.length === 0) return prev;
            const next = prev.future[0];
            const newFuture = prev.future.slice(1);
            return {
                past: [...prev.past, prev.present],
                present: next,
                future: newFuture
            };
        });
    }, []);

    const clear = useCallback(() => {
        setHistory(prev => ({
            past: [],
            present: prev.present,
            future: []
        }));
    }, []);

    return {
        state: history.present,
        set,
        undo,
        redo,
        canUndo: history.past.length > 0,
        canRedo: history.future.length > 0,
        clear
    };
}
