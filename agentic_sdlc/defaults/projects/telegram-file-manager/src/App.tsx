/**
 * Main Application Component - Responsive Layout with CSS Animations
 * @module App
 */

import { useEffect, useState, useMemo } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { FileGrid } from './components/file/FileGrid';
import { DropZone } from './components/upload/DropZone';
import { PreviewModal } from './components/dialogs/PreviewModal';
import { SettingsDialog } from './components/dialogs/SettingsDialog';
import { MobileNav, MobileHeader, SwipeableDrawer, MobileActionSheet } from './components/mobile';
import { OnboardingPage } from './pages/Onboarding';
import { useFileStore } from './store/files';
import { useSettingsStore } from './store/settings';
import { useResponsive } from './hooks/useResponsive';
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
// MOBILE NAV TAB TYPE
// ============================================================================

type MobileTab = 'home' | 'files' | 'favorites' | 'more';

// ============================================================================
// MAIN APP COMPONENT
// ============================================================================

function App() {
  const { loadFiles, loadFolders, getFilteredFiles, downloadFile, moveToTrash, toggleFavorite } = useFileStore();
  const { loadSettings, isConnected, theme, setTheme } = useSettingsStore();
  const { isMobile, isTablet } = useResponsive();

  // UI State
  const [previewFile, setPreviewFile] = useState<TelegramFile | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  // Mobile-specific state
  const [activeTab, setActiveTab] = useState<MobileTab>('home');
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [actionSheetFile, setActionSheetFile] = useState<TelegramFile | null>(null);

  // Initialize keyboard shortcuts
  useKeyboardShortcuts();

  // Get filtered files for preview navigation
  const files = useMemo(() => getFilteredFiles(), [getFilteredFiles]);

  // Load data on mount
  useEffect(() => {
    loadSettings().then(() => {
      // Only load files if already authenticated
      if (isConnected()) {
        loadFiles();
        loadFolders();
      }
    });
  }, [loadSettings, loadFiles, loadFolders, isConnected]);

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

  // Expose action sheet trigger globally (for mobile)
  useEffect(() => {
    const handleOpenActionSheet = (e: CustomEvent<TelegramFile>) => {
      setActionSheetFile(e.detail);
    };
    window.addEventListener('open-action-sheet', handleOpenActionSheet as EventListener);
    return () => window.removeEventListener('open-action-sheet', handleOpenActionSheet as EventListener);
  }, []);

  // Authentication check - show onboarding if not connected
  if (!isConnected()) {
    return <OnboardingPage />;
  }

  // Render mobile layout
  if (isMobile) {
    return (
      <div className="h-screen-mobile flex flex-col overflow-hidden animate-fade-in">
        {/* Mobile Header */}
        <MobileHeader
          onMenuClick={() => setIsDrawerOpen(true)}
        />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto pt-header pb-nav scroll-container">
          <FileGrid />
        </main>

        {/* Mobile Bottom Navigation */}
        <MobileNav
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onOpenDrawer={() => setIsDrawerOpen(true)}
        />

        {/* Swipeable Drawer */}
        <SwipeableDrawer
          isOpen={isDrawerOpen}
          onClose={() => setIsDrawerOpen(false)}
        />

        {/* Drop Zone (global) */}
        <DropZone />

        {/* Mobile Action Sheet */}
        <MobileActionSheet
          file={actionSheetFile}
          isOpen={actionSheetFile !== null}
          onClose={() => setActionSheetFile(null)}
          onDownload={downloadFile}
          onToggleFavorite={(f) => toggleFavorite(f.file_unique_id)}
          onDelete={(f) => moveToTrash([f.file_unique_id])}
        />

        {/* Preview Modal (full-screen on mobile) */}
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
      </div>
    );
  }

  // Render tablet layout (collapsible sidebar)
  if (isTablet) {
    return (
      <div className="h-screen flex overflow-hidden animate-fade-in">
        {/* Sidebar - Collapsed by default on tablet */}
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
      </div>
    );
  }

  // Render desktop layout (original)
  return (
    <div className="h-screen flex overflow-hidden animate-fade-in">
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
    </div>
  );
}

export default App;
