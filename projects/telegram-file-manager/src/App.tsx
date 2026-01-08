/**
 * Main Application Component
 * @module App
 */

import { useEffect, useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { FileGrid } from './components/file/FileGrid';
import { DropZone } from './components/upload/DropZone';
import { PreviewModal } from './components/dialogs/PreviewModal';
import { SettingsDialog } from './components/dialogs/SettingsDialog';
import { useFileStore } from './store/files';
import { useSettingsStore } from './store/settings';
import type { TelegramFile } from './lib/telegram/types';

// ============================================================================
// KEYBOARD SHORTCUTS HOOK
// ============================================================================

function useKeyboardShortcuts() {
  const { selectAll, clearSelection, selectedFiles, setViewMode, moveToTrash } = useFileStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // Ctrl/Cmd + A: Select all
      if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        e.preventDefault();
        selectAll();
      }

      // Escape: Clear selection
      if (e.key === 'Escape') {
        clearSelection();
      }

      // Delete/Backspace: Delete selected
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedFiles.length > 0) {
        e.preventDefault();
        moveToTrash(selectedFiles);
      }

      // Ctrl/Cmd + 1: Grid view
      if ((e.ctrlKey || e.metaKey) && e.key === '1') {
        e.preventDefault();
        setViewMode('grid');
      }

      // Ctrl/Cmd + 2: List view
      if ((e.ctrlKey || e.metaKey) && e.key === '2') {
        e.preventDefault();
        setViewMode('list');
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectAll, clearSelection, selectedFiles, setViewMode, moveToTrash]);
}

// ============================================================================
// MAIN APP COMPONENT
// ============================================================================

function App() {
  const { loadFiles, loadFolders, getFilteredFiles, downloadFile, moveToTrash, toggleFavorite } = useFileStore();
  const { loadSettings, telegram, theme, setTheme } = useSettingsStore();

  // Modals
  const [previewFile, setPreviewFile] = useState<TelegramFile | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  // Initialize keyboard shortcuts
  useKeyboardShortcuts();

  // Get filtered files for preview navigation
  const files = useMemo(() => getFilteredFiles(), [getFilteredFiles]);

  // Load data on mount
  useEffect(() => {
    loadSettings().then(() => {
      loadFiles();
      loadFolders();
    });
  }, [loadSettings, loadFiles, loadFolders]);

  // Apply theme
  useEffect(() => {
    setTheme(theme);
  }, [theme, setTheme]);

  // Expose settings toggle globally
  useEffect(() => {
    const handleOpenSettings = () => setShowSettings(true);
    window.addEventListener('open-settings', handleOpenSettings);
    return () => window.removeEventListener('open-settings', handleOpenSettings);
  }, []);

  // Expose preview trigger globally
  useEffect(() => {
    const handlePreviewFile = (e: CustomEvent<TelegramFile>) => {
      setPreviewFile(e.detail);
    };
    window.addEventListener('preview-file', handlePreviewFile as EventListener);
    return () => window.removeEventListener('preview-file', handlePreviewFile as EventListener);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-screen flex overflow-hidden"
    >
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />

        {/* File Grid */}
        <FileGrid />
      </div>

      {/* Drop Zone (global) */}
      <DropZone />

      {/* Preview Modal */}
      <PreviewModal
        file={previewFile}
        files={files}
        isOpen={previewFile !== null}
        onClose={() => setPreviewFile(null)}
        onDownload={downloadFile}
        onDelete={(f) => moveToTrash([f.file_unique_id])}
        onToggleFavorite={(f) => toggleFavorite(f.file_unique_id)}
        onNavigate={setPreviewFile}
      />

      {/* Settings Dialog */}
      <SettingsDialog
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />

      {/* Connection Status Banner */}
      {!telegram?.is_connected && (
        <button
          onClick={() => setShowSettings(true)}
          className="fixed bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full text-sm cursor-pointer transition-all hover:scale-105"
          style={{
            background: 'rgba(234, 179, 8, 0.2)',
            border: '1px solid rgba(234, 179, 8, 0.3)',
            color: '#fbbf24',
          }}
        >
          Demo Mode - Click to connect Telegram
        </button>
      )}
    </motion.div>
  );
}

export default App;
