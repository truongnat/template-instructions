import { AlertTriangle, X, Copy, RefreshCw, FileText } from 'lucide-react';
import { Button } from './ui/button';
import { useState } from 'react';

interface FFmpegError {
    code?: string;
    message: string;
    details?: string;
    command?: string;
}

interface ErrorDialogProps {
    error: FFmpegError | null;
    onClose: () => void;
    onRetry?: () => void;
}

// Common FFmpeg error patterns and their user-friendly messages
const ERROR_PATTERNS: { pattern: RegExp; title: string; suggestion: string }[] = [
    {
        pattern: /No such file or directory/i,
        title: 'File Not Found',
        suggestion: 'The input file may have been moved or deleted. Try opening the file again.'
    },
    {
        pattern: /Permission denied/i,
        title: 'Permission Denied',
        suggestion: 'The application doesn\'t have permission to access this file. Try running as administrator or choosing a different location.'
    },
    {
        pattern: /Invalid data found/i,
        title: 'Corrupted File',
        suggestion: 'The input file appears to be corrupted or in an unsupported format. Try re-downloading or converting the source file.'
    },
    {
        pattern: /codec not found|encoder.*not found/i,
        title: 'Missing Codec',
        suggestion: 'FFmpeg is missing a required codec. Try installing the full FFmpeg build or choosing a different output format.'
    },
    {
        pattern: /output file.*already exists/i,
        title: 'File Already Exists',
        suggestion: 'The output file already exists. Choose a different filename or delete the existing file.'
    },
    {
        pattern: /out of memory|cannot allocate/i,
        title: 'Out of Memory',
        suggestion: 'Not enough memory to process this file. Try closing other applications or reducing the output resolution.'
    },
    {
        pattern: /timeout|timed out/i,
        title: 'Operation Timed Out',
        suggestion: 'The operation took too long. Try with a shorter clip or lower quality settings.'
    },
    {
        pattern: /Cancelled by user/i,
        title: 'Cancelled',
        suggestion: 'The operation was cancelled by the user.'
    }
];

function parseError(error: FFmpegError): { title: string; suggestion: string } {
    const fullMessage = `${error.message} ${error.details || ''}`;

    for (const { pattern, title, suggestion } of ERROR_PATTERNS) {
        if (pattern.test(fullMessage)) {
            return { title, suggestion };
        }
    }

    return {
        title: 'Conversion Failed',
        suggestion: 'An unexpected error occurred. Check the error details below for more information.'
    };
}

export function ErrorDialog({ error, onClose, onRetry }: ErrorDialogProps) {
    const [showDetails, setShowDetails] = useState(false);
    const [copied, setCopied] = useState(false);

    if (!error) return null;

    const { title, suggestion } = parseError(error);

    const copyToClipboard = async () => {
        const errorText = `
FFmpeg Error Report
===================
Error: ${error.message}
${error.details ? `Details: ${error.details}` : ''}
${error.command ? `Command: ${error.command}` : ''}
Time: ${new Date().toISOString()}
        `.trim();

        await navigator.clipboard.writeText(errorText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="dialog-overlay" onClick={onClose}>
            <div className="dialog error-dialog" onClick={e => e.stopPropagation()}>
                <div className="dialog-header error-header">
                    <h2><AlertTriangle size={20} /> {title}</h2>
                    <Button variant="ghost" size="icon" onClick={onClose}>
                        <X size={20} />
                    </Button>
                </div>

                <div className="dialog-content">
                    <div className="error-suggestion">
                        <p>{suggestion}</p>
                    </div>

                    <div className="error-message">
                        <strong>Error:</strong> {error.message}
                    </div>

                    {(error.details || error.command) && (
                        <div className="error-details-toggle">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowDetails(!showDetails)}
                            >
                                <FileText size={14} className="mr-2" />
                                {showDetails ? 'Hide Details' : 'Show Details'}
                            </Button>
                        </div>
                    )}

                    {showDetails && (
                        <div className="error-details">
                            {error.details && (
                                <div className="error-detail-section">
                                    <label>Details:</label>
                                    <pre>{error.details}</pre>
                                </div>
                            )}
                            {error.command && (
                                <div className="error-detail-section">
                                    <label>Command:</label>
                                    <pre>{error.command}</pre>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div className="dialog-footer error-footer">
                    <Button variant="secondary" onClick={copyToClipboard}>
                        <Copy size={14} className="mr-2" /> {copied ? 'Copied!' : 'Copy Error'}
                    </Button>
                    {onRetry && (
                        <Button onClick={onRetry}>
                            <RefreshCw size={14} className="mr-2" /> Retry
                        </Button>
                    )}
                    <Button onClick={onClose}>
                        Close
                    </Button>
                </div>
            </div>
        </div>
    );
}

export type { FFmpegError };
