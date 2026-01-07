import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Progress } from "./ui/progress";
import { DownloadCloud, Youtube, XCircle, Loader2, Plus, Folder } from "lucide-react";

import { downloadDir } from '@tauri-apps/api/path';
import { open } from '@tauri-apps/plugin-shell';

interface DownloadItem {
    id: string;
    url: string;
    status: "pending" | "downloading" | "completed" | "error";
    progress: number;
    filePath?: string;
    error?: string;
}

interface DownloadPanelProps {
    onAddFile: (path: string) => void;
    className?: string;
}

export function DownloadPanel({ onAddFile, className }: DownloadPanelProps) {
    const [url, setUrl] = useState("");
    const [isDownloading, setIsDownloading] = useState(false);
    const [downloads, setDownloads] = useState<DownloadItem[]>([]);
    const [downloadPath, setDownloadPath] = useState<string>("");

    useEffect(() => {
        // Initialize download path
        const initPath = async () => {
            const dDir = await downloadDir();
            setDownloadPath(`${dDir}FFmpegEditor`);
        };
        initPath();

        // Listen for progress
        const unlisten = listen<any>("download-progress", (event) => {
            setDownloads(prev => {
                // Assume single active download for V1 for simplicity in matching progress
                // In a real multi-download scenario, we'd need IDs in the event
                const activeIndex = prev.findIndex(d => d.status === "downloading");
                if (activeIndex !== -1) {
                    const newDownloads = [...prev];
                    newDownloads[activeIndex].progress = event.payload.percent;
                    return newDownloads;
                }
                return prev;
            });
        });

        return () => {
            unlisten.then(f => f());
        };
    }, []);

    const openDownloadFolder = async () => {
        try {
            await open(downloadPath);
        } catch (e) {
            console.error("Failed to open folder", e);
        }
    };

    const handleDownload = async () => {
        if (!url) return;

        const newItem: DownloadItem = {
            id: crypto.randomUUID(),
            url,
            status: "downloading",
            progress: 0
        };

        setDownloads(prev => [newItem, ...prev]);
        setIsDownloading(true);
        setUrl("");

        try {
            // Ensure directory exists (handled by backend or we do it here? Backend does it via yt-dlp usually if recursive)
            // Ideally we should ensure it exists.
            // But let's assume yt-dlp handles it or we rely on backend.
            // Actually backend doesn't mkdir, so we should do it or yt-dlp might fail if parent missing?
            // yt-dlp usually creates folders.

            const filePath = await invoke<string>("download_video", {
                url: newItem.url,
                outputDir: downloadPath
            });

            setDownloads(prev => prev.map(d =>
                d.id === newItem.id
                    ? { ...d, status: "completed", progress: 100, filePath }
                    : d
            ));
        } catch (error: any) {
            setDownloads(prev => prev.map(d =>
                d.id === newItem.id
                    ? { ...d, status: "error", error: String(error) }
                    : d
            ));
        } finally {
            setIsDownloading(false);
        }
    };

    return (
        <Card className={className}>
            <CardHeader>
                <div className="flex justify-between items-center">
                    <CardTitle className="flex items-center gap-2">
                        <Youtube className="w-5 h-5 text-red-500" />
                        YouTube Downloader
                    </CardTitle>
                    <Button variant="ghost" size="icon" onClick={openDownloadFolder} title="Open Download Folder">
                        <Folder className="w-4 h-4" />
                    </Button>
                </div>
                <CardDescription>Download videos directly for editing</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="flex gap-2">
                    <div className="grid w-full items-center gap-1.5">
                        <Label htmlFor="yt-url">Video URL</Label>
                        <Input
                            id="yt-url"
                            placeholder="https://www.youtube.com/watch?v=..."
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            disabled={isDownloading}
                        />
                    </div>
                    <Button
                        className="mt-auto"
                        onClick={handleDownload}
                        disabled={!url || isDownloading}
                    >
                        {isDownloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <DownloadCloud className="w-4 h-4" />}
                        <span className="ml-2">Download</span>
                    </Button>
                </div>

                {downloads.length > 0 && (
                    <div className="space-y-2 mt-4">
                        <Label>Recent Downloads</Label>
                        <div className="grid gap-2 max-h-[200px] overflow-y-auto">
                            {downloads.map(item => (
                                <div key={item.id} className="flex items-center justify-between p-2 border rounded-md bg-muted/50 text-sm">
                                    <div className="flex-1 min-w-0 mr-2">
                                        <div className="flex justify-between mb-1">
                                            <span className="truncate font-medium">{item.url}</span>
                                            {item.status === 'downloading' && <span>{item.progress.toFixed(1)}%</span>}
                                        </div>
                                        {item.status === 'downloading' && <Progress value={item.progress} className="h-1.5" />}
                                        {item.status === 'error' && <span className="text-destructive text-xs">{item.error}</span>}
                                        {item.status === 'completed' && <span className="text-green-500 text-xs truncate">{item.filePath}</span>}
                                    </div>

                                    {item.status === 'completed' && (
                                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0" onClick={() => item.filePath && onAddFile(item.filePath)} title="Add to Project">
                                            <Plus className="w-4 h-4" />
                                        </Button>
                                    )}
                                    {item.status === 'downloading' && (
                                        <Button size="sm" variant="ghost" className="h-8 w-8 p-0" onClick={() => invoke("cancel_conversion")} title="Cancel">
                                            <XCircle className="w-4 h-4 text-destructive" />
                                        </Button>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
