import { X } from 'lucide-react';
import { Button } from './ui/button';

interface MergeDialogProps {
    queue: string[];
    onClose: () => void;
    onRemove: (index: number) => void;
    onAddMore: () => void;
    onMerge: () => void;
    isConverting: boolean;
}

export function MergeDialog({
    queue,
    onClose,
    onRemove,
    onAddMore,
    onMerge,
    isConverting
}: MergeDialogProps) {
    return (
        <div className="modal-overlay">
            <div className="modal">
                <div className="modal-header">
                    <h2>Merge clips</h2>
                    <Button variant="ghost" size="icon" onClick={onClose} disabled={isConverting}>
                        <X size={20} />
                    </Button>
                </div>

                <div className="modal-body">
                    <p style={{ marginBottom: '12px', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                        Files will be concatenated in the order shown below. All files must have the same resolution and codecs for "fast merge".
                    </p>
                    <div className="batch-list">
                        {queue.map((file, idx) => (
                            <div key={idx} className="batch-item">
                                <span className="batch-item-path">{file.split(/[\\/]/).pop()}</span>
                                <Button
                                    onClick={() => onRemove(idx)}
                                    variant="ghost"
                                    size="icon"
                                    disabled={isConverting}
                                >
                                    <X size={14} />
                                </Button>
                            </div>
                        ))}
                    </div>
                    <Button
                        onClick={onAddMore}
                        variant="secondary"
                        className="w-full mt-3 justify-center"
                        disabled={isConverting}
                    >
                        + Add More Files
                    </Button>
                </div>

                <div className="modal-footer">
                    <Button onClick={onClose} variant="secondary" disabled={isConverting}>
                        Cancel
                    </Button>
                    <Button
                        onClick={onMerge}
                        disabled={queue.length < 2 || isConverting}
                    >
                        {isConverting ? 'Merging...' : `Merge ${queue.length} Files`}
                    </Button>
                </div>
            </div>
        </div>
    );
}
