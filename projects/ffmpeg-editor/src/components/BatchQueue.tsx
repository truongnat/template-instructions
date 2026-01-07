import { Settings, X } from 'lucide-react';
import { Button } from './ui/button';
import { ConvertOptions } from '../types';

interface BatchQueueProps {
    queue: ConvertOptions[];
    onRemove: (index: number) => void;
    onProcess: () => void;
    isProcessing: boolean;
}

export function BatchQueue({ queue, onRemove, onProcess, isProcessing }: BatchQueueProps) {
    if (queue.length === 0) return null;

    return (
        <div className="batch-queue">
            <h3><Settings size={16} /> Batch Queue ({queue.length})</h3>
            <div className="batch-list">
                {queue.map((item, idx) => (
                    <div key={idx} className="batch-item">
                        <div className="batch-item-info">
                            <span className="batch-item-path">{item.input.split(/[\\/]/).pop()}</span>
                            <span className="batch-item-meta">
                                {item.video_codec} • {item.width ? `${item.width}x${item.height}` : 'Original'}
                            </span>
                        </div>
                        <Button
                            onClick={() => onRemove(idx)}
                            variant="ghost"
                            size="icon"
                            disabled={isProcessing}
                        >
                            <X size={14} />
                        </Button>
                    </div>
                ))}
            </div>
            <div className="batch-actions" style={{ marginTop: '12px' }}>
                <Button
                    onClick={onProcess}
                    disabled={isProcessing}
                    className="w-full justify-center"
                >
                    {isProcessing ? 'Processing Batch...' : 'Start Batch Process'}
                </Button>
            </div>
        </div>
    );
}
