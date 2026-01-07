import React from 'react';
import { OverlaySettings } from '../types';
import { Type, Image as ImageIcon, X } from 'lucide-react';
import { Button } from './ui/button';
import { open } from '@tauri-apps/plugin-dialog';

interface OverlayPanelProps {
    overlays: OverlaySettings;
    onChange: (overlays: OverlaySettings) => void;
}

export const OverlayPanel: React.FC<OverlayPanelProps> = ({ overlays, onChange }) => {
    const handleTextChange = (key: string, value: any) => {
        onChange({
            ...overlays,
            text: {
                ...(overlays.text || { content: '', fontSize: 24, color: 'white', x: '10', y: '10' }),
                [key]: value
            }
        });
    };

    const handleImageChange = (key: string, value: any) => {
        onChange({
            ...overlays,
            image: {
                ...(overlays.image || { path: '', x: '(W-w)-10', y: '(H-h)-10', opacity: 1 }),
                [key]: value
            }
        });
    };

    const selectImage = async () => {
        const file = await open({
            multiple: false,
            filters: [{ name: 'Images', extensions: ['png', 'jpg', 'jpeg'] }]
        });
        if (file) handleImageChange('path', file as string);
    };

    return (
        <div className="panel overlay-panel">
            <div className="panel-header">
                <h3>Overlays</h3>
            </div>

            <div className="overlay-section">
                <label className="section-title"><Type size={14} /> Text Watermark</label>
                <div className="input-row">
                    <input
                        type="text"
                        placeholder="Enter text..."
                        value={overlays.text?.content || ''}
                        onChange={(e) => handleTextChange('content', e.target.value)}
                    />
                    {overlays.text && (
                        <Button variant="ghost" size="icon" onClick={() => onChange({ ...overlays, text: undefined })}>
                            <X size={14} />
                        </Button>
                    )}
                </div>
                {overlays.text && (
                    <div className="details grid2">
                        <div>
                            <label>Size</label>
                            <input
                                type="number"
                                value={overlays.text.fontSize}
                                onChange={(e) => handleTextChange('fontSize', parseInt(e.target.value))}
                            />
                        </div>
                        <div>
                            <label>Color</label>
                            <input
                                type="text"
                                value={overlays.text.color}
                                onChange={(e) => handleTextChange('color', e.target.value)}
                            />
                        </div>
                        <div>
                            <label>X Pos</label>
                            <input
                                type="text"
                                value={overlays.text.x}
                                onChange={(e) => handleTextChange('x', e.target.value)}
                            />
                        </div>
                        <div>
                            <label>Y Pos</label>
                            <input
                                type="text"
                                value={overlays.text.y}
                                onChange={(e) => handleTextChange('y', e.target.value)}
                            />
                        </div>
                    </div>
                )}
            </div>

            <div className="overlay-section">
                <label className="section-title"><ImageIcon size={14} /> Image Overlay (Logo)</label>
                {!overlays.image?.path ? (
                    <Button variant="secondary" size="sm" onClick={selectImage}>
                        Select Image
                    </Button>
                ) : (
                    <div className="image-info">
                        <div className="input-row">
                            <span className="file-name">{overlays.image.path.split(/[\\/]/).pop()}</span>
                            <Button variant="ghost" size="icon" onClick={() => selectImage()}>
                                <ImageIcon size={14} />
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => onChange({ ...overlays, image: undefined })}>
                                <X size={14} />
                            </Button>
                        </div>
                        <div className="details grid2">
                            <div>
                                <label>X Pos</label>
                                <input
                                    type="text"
                                    value={overlays.image.x}
                                    onChange={(e) => handleImageChange('x', e.target.value)}
                                />
                            </div>
                            <div>
                                <label>Y Pos</label>
                                <input
                                    type="text"
                                    value={overlays.image.y}
                                    onChange={(e) => handleImageChange('y', e.target.value)}
                                />
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
