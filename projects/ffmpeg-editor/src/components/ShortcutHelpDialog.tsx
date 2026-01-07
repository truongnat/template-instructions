import { X, Keyboard } from 'lucide-react';
import { Button } from './ui/button';
import { SHORTCUT_DEFINITIONS, formatShortcut } from '../hooks/useKeyboardShortcuts';

interface ShortcutHelpDialogProps {
    isOpen: boolean;
    onClose: () => void;
}

export function ShortcutHelpDialog({ isOpen, onClose }: ShortcutHelpDialogProps) {
    if (!isOpen) return null;

    // Group shortcuts by category
    const playbackShortcuts = SHORTCUT_DEFINITIONS.filter(s =>
        ['onPlayPause', 'onFrameBack', 'onFrameForward'].includes(s.action)
    );
    const editingShortcuts = SHORTCUT_DEFINITIONS.filter(s =>
        ['onSetIn', 'onSetOut', 'onUndo', 'onRedo'].includes(s.action)
    );
    const fileShortcuts = SHORTCUT_DEFINITIONS.filter(s =>
        ['onOpenFile', 'onExport', 'onEscape'].includes(s.action)
    );

    return (
        <div className="dialog-overlay" onClick={onClose}>
            <div className="dialog shortcut-dialog" onClick={e => e.stopPropagation()}>
                <div className="dialog-header">
                    <h2><Keyboard size={20} /> Keyboard Shortcuts</h2>
                    <Button variant="ghost" size="icon" onClick={onClose}>
                        <X size={20} />
                    </Button>
                </div>

                <div className="dialog-content">
                    <div className="shortcut-section">
                        <h3>Playback</h3>
                        <div className="shortcut-list">
                            {playbackShortcuts.map((shortcut, idx) => (
                                <div key={idx} className="shortcut-row">
                                    <span className="shortcut-desc">{shortcut.description}</span>
                                    <kbd className="shortcut-key">{formatShortcut(shortcut)}</kbd>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="shortcut-section">
                        <h3>Editing</h3>
                        <div className="shortcut-list">
                            {editingShortcuts.map((shortcut, idx) => (
                                <div key={idx} className="shortcut-row">
                                    <span className="shortcut-desc">{shortcut.description}</span>
                                    <kbd className="shortcut-key">{formatShortcut(shortcut)}</kbd>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="shortcut-section">
                        <h3>File Operations</h3>
                        <div className="shortcut-list">
                            {fileShortcuts.map((shortcut, idx) => (
                                <div key={idx} className="shortcut-row">
                                    <span className="shortcut-desc">{shortcut.description}</span>
                                    <kbd className="shortcut-key">{formatShortcut(shortcut)}</kbd>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="dialog-footer">
                    <Button onClick={onClose}>
                        Got it!
                    </Button>
                </div>
            </div>
        </div>
    );
}
