'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  HardDrive,
  Folder,
  File as FileIcon,
  FileText,
  FileImage,
  FileVideo,
  FileAudio,
  Search,
  Plus,
  Upload,
  Trash2,
  Download,
  ChevronRight,
  Loader2,
  Link2,
  Link2Off,
  FolderPlus,
  RefreshCw,
} from 'lucide-react';
import { api, getAccessToken } from '@/lib/api';

interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  size?: string;
  modifiedTime: string;
  thumbnailLink?: string;
  iconLink?: string;
}

interface Breadcrumb {
  id: string;
  name: string;
}

export default function StoragePage() {
  // Status states
  const [isConfigured, setIsConfigured] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [connectedEmail, setConnectedEmail] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // File browser states
  const [files, setFiles] = useState<DriveFile[]>([]);
  const [currentFolder, setCurrentFolder] = useState<string>('root');
  const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([{ id: 'root', name: 'Root' }]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  // UI operation states
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [isCreatingFolder, setIsCreatingFolder] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sync / Backup states
  const [syncing, setSyncing] = useState<Record<string, boolean>>({});
  const [restoring, setRestoring] = useState<Record<string, boolean>>({});

  const handleSyncSection = async (section: string) => {
    setSyncing((prev) => ({ ...prev, [section]: true }));
    try {
      const response = await api<{ status: string; message: string }>(`/api/gdrive/sync/${section}`, {
        method: 'POST',
      });
      alert(response.message);
    } catch (err) {
      alert(`Sync failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setSyncing((prev) => ({ ...prev, [section]: false }));
    }
  };

  const handleRestoreSection = async (section: string) => {
    if (
      confirm(
        `Are you sure you want to RESTORE ${section} from Google Drive? This will overwrite your local database records for this section.`
      )
    ) {
      setRestoring((prev) => ({ ...prev, [section]: true }));
      try {
        const response = await api<{ status: string; message: string }>(
          `/api/gdrive/restore/${section}`,
          {
            method: 'POST',
          }
        );
        alert(response.message);
      } catch (err) {
        alert(`Restore failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
      } finally {
        setRestoring((prev) => ({ ...prev, [section]: false }));
      }
    }
  };

  // Load files in active folder
  const loadFiles = useCallback(async (folderId: string, searchVal = '') => {
    setLoading(true);
    try {
      let endpoint = `/api/gdrive/files?folder_id=${folderId}`;
      if (searchVal) {
        endpoint = `/api/gdrive/files?q=${encodeURIComponent(searchVal)}`;
        setIsSearching(true);
      } else {
        setIsSearching(false);
      }

      const data = await api<{ files: DriveFile[] }>(endpoint);
      setFiles(data.files || []);
    } catch (error) {
      console.error('Failed to load Google Drive files:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load configuration & status
  const checkStatus = useCallback(async () => {
    try {
      const data = await api<{ configured: boolean; connected: boolean; email: string | null }>(
        '/api/gdrive/status'
      );
      setIsConfigured(data.configured);
      setIsConnected(data.connected);
      setConnectedEmail(data.email);

      if (data.connected) {
        await loadFiles(currentFolder);
      }
    } catch (error) {
      console.error('Failed to get Google Drive status:', error);
    } finally {
      setLoading(false);
    }
  }, [currentFolder, loadFiles]);

  useEffect(() => {
    checkStatus();
  }, [currentFolder, checkStatus]);

  // Initiate OAuth login flow
  const handleConnect = async () => {
    try {
      const data = await api<{ url: string }>('/api/gdrive/auth-url');
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      alert('Failed to start connection flow. Make sure Google Client credentials are set in .env');
      console.error(error);
    }
  };

  // Disconnect from Google Drive
  const handleDisconnect = async () => {
    if (confirm('Are you sure you want to disconnect Google Drive? This will unlink your storage but won\'t delete any files in your Google Drive.')) {
      setLoading(true);
      try {
        await api('/api/gdrive/disconnect', { method: 'POST' });
        setIsConnected(false);
        setConnectedEmail(null);
        setFiles([]);
        setBreadcrumbs([{ id: 'root', name: 'Root' }]);
        setCurrentFolder('root');
      } catch (error) {
        console.error('Failed to disconnect Google Drive:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  // Folder navigation
  const handleFolderClick = (folder: DriveFile) => {
    const nextFolder = folder.id;
    setCurrentFolder(nextFolder);
    setBreadcrumbs((prev) => [...prev, { id: folder.id, name: folder.name }]);
  };

  const handleBreadcrumbClick = (crumb: Breadcrumb, index: number) => {
    setCurrentFolder(crumb.id);
    setBreadcrumbs((prev) => prev.slice(0, index + 1));
    setSearchQuery('');
  };

  // Search files
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadFiles(currentFolder, searchQuery);
  };

  const clearSearch = () => {
    setSearchQuery('');
    loadFiles(currentFolder, '');
  };

  // Create folder
  const handleCreateFolder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFolderName.trim()) return;

    setIsCreatingFolder(true);
    try {
      await api('/api/gdrive/folders', {
        method: 'POST',
        body: {
          name: newFolderName,
          parent_id: currentFolder,
        },
      });
      setNewFolderName('');
      setShowFolderModal(false);
      await loadFiles(currentFolder);
    } catch (error) {
      alert('Failed to create folder.');
      console.error(error);
    } finally {
      setIsCreatingFolder(false);
    }
  };

  // Upload file
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (!selectedFiles || selectedFiles.length === 0) return;

    const file = selectedFiles[0];
    const formData = new FormData();
    formData.append('file', file);
    if (currentFolder && currentFolder !== 'root') {
      formData.append('parent_id', currentFolder);
    }

    setIsUploading(true);
    setUploadProgress(`Uploading "${file.name}"...`);

    try {
      const token = getAccessToken();
      const headers: HeadersInit = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch('/api/gdrive/upload', {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload request failed');
      }

      setUploadProgress('Upload complete!');
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(null);
        loadFiles(currentFolder);
      }, 1000);
    } catch (error) {
      alert(`Failed to upload file "${file.name}"`);
      console.error(error);
      setIsUploading(false);
      setUploadProgress(null);
    }
  };

  // Download file
  const handleDownload = async (file: DriveFile) => {
    try {
      const response = await fetch(`/api/gdrive/files/${file.id}/download`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      // Read Content-Disposition header if available
      const disposition = response.headers.get('Content-Disposition');
      let filename = file.name;
      if (disposition && disposition.indexOf('filename=') !== -1) {
        const matches = /filename="([^"]+)"/.exec(disposition);
        if (matches != null && matches[1]) {
          filename = matches[1];
        }
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Failed to download file.');
      console.error(error);
    }
  };

  // Delete file
  const handleDelete = async (file: DriveFile) => {
    if (confirm(`Are you sure you want to delete "${file.name}"? This will move it to trash or permanently delete it.`)) {
      try {
        await api(`/api/gdrive/files/${file.id}`, { method: 'DELETE' });
        await loadFiles(currentFolder);
      } catch (error) {
        alert('Failed to delete file.');
        console.error(error);
      }
    }
  };

  // File type helpers
  const formatBytes = (bytesStr?: string) => {
    if (!bytesStr) return '—';
    const bytes = parseInt(bytesStr, 10);
    if (isNaN(bytes)) return '—';
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType === 'application/vnd.google-apps.folder') return <Folder className="h-5 w-5 text-amber-500 fill-amber-500/20" />;
    if (mimeType.startsWith('image/')) return <FileImage className="h-5 w-5 text-emerald-400" />;
    if (mimeType.startsWith('video/')) return <FileVideo className="h-5 w-5 text-blue-400" />;
    if (mimeType.startsWith('audio/')) return <FileAudio className="h-5 w-5 text-violet-400" />;
    if (mimeType.includes('pdf') || mimeType.includes('document')) return <FileText className="h-5 w-5 text-rose-400" />;
    return <FileIcon className="h-5 w-5 text-muted-foreground" />;
  };

  const isFolder = (mimeType: string) => mimeType === 'application/vnd.google-apps.folder';

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <HardDrive className="h-7 w-7 text-primary animate-pulse" />
            Cloud Storage
          </h1>
          <p className="text-sm text-muted-foreground">
            Manage your Google Drive files and upload media assets (5 TB subscription).
          </p>
        </div>

        {isConfigured && isConnected && (
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground border border-border rounded-full px-3 py-1 bg-muted flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              {connectedEmail || 'Connected'}
            </span>
            <button
              onClick={handleDisconnect}
              className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-destructive hover:bg-destructive/10 transition-colors flex items-center gap-1"
            >
              <Link2Off className="h-3.5 w-3.5" />
              Disconnect
            </button>
          </div>
        )}
      </div>

      {/* Loading Overlay */}
      {loading && files.length === 0 && (
        <div className="flex min-h-[40vh] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      )}

      {/* 1. Google Cloud APIs NOT Configured Banner */}
      {!loading && !isConfigured && (
        <div className="rounded-xl border border-warning/30 bg-warning/5 p-6 text-warning-foreground">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-amber-500">
            Google Drive Credentials Not Found
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            To use this feature, you must configure the Google OAuth credentials in your API server env files.
          </p>
          <div className="mt-4 text-xs font-mono bg-card/65 p-4 border border-border rounded-lg max-w-2xl text-foreground">
            <p className="font-semibold text-primary mb-1">Add to apps/api/.env:</p>
            <p>GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com</p>
            <p>GOOGLE_CLIENT_SECRET=your_client_secret</p>
            <p>GOOGLE_REDIRECT_URI=http://localhost:3000/storage/callback</p>
          </div>
        </div>
      )}

      {/* 2. Configured but NOT Connected Dashboard */}
      {!loading && isConfigured && !isConnected && (
        <div className="flex flex-col items-center justify-center border border-border rounded-xl bg-card/40 p-12 text-center min-h-[45vh] shadow-sm">
          <div className="rounded-full bg-primary/10 p-4 mb-4">
            <HardDrive className="h-12 w-12 text-primary" />
          </div>
          <h2 className="text-xl font-bold tracking-tight text-foreground">Connect your Cloud Storage</h2>
          <p className="mt-2 text-sm text-muted-foreground max-w-md">
            Integrate your dashboard with Google Drive to access your 5 TB cloud vault. Upload files, manage media assets, and build your AI knowledge base.
          </p>
          <button
            onClick={handleConnect}
            className="mt-6 rounded-md bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground shadow-md hover:bg-primary/95 transition-all flex items-center gap-2"
          >
            <Link2 className="h-4 w-4" />
            Connect Google Drive
          </button>
        </div>
      )}

      {/* 2.5 Google Drive Sync Panel */}
      {isConnected && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {['notes', 'finance', 'books', 'habits'].map((section) => (
            <div key={section} className="glass-card p-4 flex flex-col justify-between gap-3 text-left">
              <div>
                <h3 className="text-xs font-bold text-foreground capitalize flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-primary"></span>
                  {section} Sync
                </h3>
                <p className="text-3xs text-muted-foreground mt-1">
                  Backup local {section} database records to Google Drive or restore from cloud.
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleSyncSection(section)}
                  disabled={syncing[section]}
                  className="flex-1 rounded border border-border hover:border-primary px-2.5 py-1 text-3xs text-foreground font-semibold text-center hover:bg-primary/5 transition-colors disabled:opacity-50 inline-flex justify-center items-center gap-1"
                >
                  {syncing[section] ? (
                    <Loader2 className="h-3 w-3 animate-spin text-primary" />
                  ) : (
                    'Backup'
                  )}
                </button>
                <button
                  onClick={() => handleRestoreSection(section)}
                  disabled={restoring[section]}
                  className="flex-1 rounded bg-primary hover:bg-primary/95 px-2.5 py-1 text-3xs text-primary-foreground font-semibold text-center transition-colors disabled:opacity-50 inline-flex justify-center items-center gap-1"
                >
                  {restoring[section] ? (
                    <Loader2 className="h-3 w-3 animate-spin text-primary-foreground" />
                  ) : (
                    'Restore'
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 3. Connected Storage Browser */}
      {isConnected && (
        <div className="flex flex-col gap-4 border border-border rounded-xl bg-card p-4 shadow-sm">
          
          {/* Operations Bar */}
          <div className="flex flex-col sm:flex-row gap-3 items-center justify-between border-b border-border pb-4">
            {/* Search */}
            <form onSubmit={handleSearch} className="relative w-full sm:w-80">
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-md border border-border bg-background py-1.5 pl-8 pr-8 text-sm outline-none focus:border-primary transition-colors text-foreground"
              />
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
              {searchQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-2.5 top-2.5 text-xs text-muted-foreground hover:text-foreground"
                >
                  Clear
                </button>
              )}
            </form>

            {/* Folder Actions */}
            <div className="flex gap-2 w-full sm:w-auto justify-end">
              <button
                onClick={() => setShowFolderModal(true)}
                className="rounded-md border border-border bg-card hover:bg-accent px-3 py-1.5 text-xs font-semibold text-foreground flex items-center gap-1.5 transition-colors"
              >
                <FolderPlus className="h-3.5 w-3.5" />
                New Folder
              </button>
              <button
                onClick={handleUploadClick}
                disabled={isUploading}
                className="rounded-md bg-primary hover:bg-primary/90 px-3 py-1.5 text-xs font-semibold text-primary-foreground flex items-center gap-1.5 transition-colors"
              >
                {isUploading ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Upload className="h-3.5 w-3.5" />
                )}
                Upload File
              </button>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
              />
            </div>
          </div>

          {/* Upload Progress Alert */}
          {isUploading && uploadProgress && (
            <div className="rounded-lg bg-primary/10 border border-primary/20 p-3 text-xs text-primary flex items-center gap-2">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              {uploadProgress}
            </div>
          )}

          {/* Breadcrumb Path */}
          <div className="flex items-center gap-1 flex-wrap text-xs font-medium text-muted-foreground py-1 bg-muted/30 px-2 rounded-md">
            {breadcrumbs.map((crumb, idx) => (
              <div key={crumb.id} className="flex items-center gap-1">
                {idx > 0 && <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/50" />}
                <button
                  onClick={() => handleBreadcrumbClick(crumb, idx)}
                  className={`hover:text-foreground transition-colors ${
                    idx === breadcrumbs.length - 1 ? 'text-foreground font-semibold' : ''
                  }`}
                >
                  {crumb.name}
                </button>
              </div>
            ))}
            {isSearching && (
              <span className="text-primary ml-2 font-semibold">
                (Search results for &quot;{searchQuery}&quot;)
              </span>
            )}
            <button
              onClick={() => loadFiles(currentFolder, searchQuery)}
              className="ml-auto p-1 hover:bg-accent rounded-full transition-colors text-muted-foreground hover:text-foreground"
              title="Refresh list"
            >
              <RefreshCw className="h-3 w-3" />
            </button>
          </div>

          {/* Directory Files Grid/List */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border text-muted-foreground font-medium select-none">
                  <th className="py-2.5 pl-2 font-semibold">Name</th>
                  <th className="py-2.5 font-semibold hidden md:table-cell">Modified</th>
                  <th className="py-2.5 font-semibold text-right pr-6 hidden sm:table-cell">Size</th>
                  <th className="py-2.5 font-semibold text-right pr-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {files.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-12 text-center text-muted-foreground">
                      This folder is empty.
                    </td>
                  </tr>
                ) : (
                  files.map((file) => (
                    <tr
                      key={file.id}
                      className="border-b border-border/50 hover:bg-muted/40 transition-colors group"
                    >
                      <td className="py-3 pl-2 max-w-xs md:max-w-md truncate">
                        {isFolder(file.mimeType) ? (
                          <button
                            onClick={() => handleFolderClick(file)}
                            className="flex items-center gap-3 text-left font-medium hover:text-primary hover:underline outline-none text-foreground"
                          >
                            {getFileIcon(file.mimeType)}
                            <span className="truncate">{file.name}</span>
                          </button>
                        ) : (
                          <div className="flex items-center gap-3 text-muted-foreground">
                            {getFileIcon(file.mimeType)}
                            <span className="truncate font-medium text-foreground">{file.name}</span>
                          </div>
                        )}
                      </td>
                      <td className="py-3 text-muted-foreground hidden md:table-cell">
                        {new Date(file.modifiedTime).toLocaleDateString(undefined, {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="py-3 text-right pr-6 text-muted-foreground hidden sm:table-cell">
                        {formatBytes(file.size)}
                      </td>
                      <td className="py-3 text-right pr-4">
                        <div className="inline-flex gap-1">
                          {!isFolder(file.mimeType) && (
                            <button
                              onClick={() => handleDownload(file)}
                              className="p-1.5 rounded hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
                              title="Download"
                            >
                              <Download className="h-3.5 w-3.5" />
                            </button>
                          )}
                          <button
                            onClick={() => handleDelete(file)}
                            className="p-1.5 rounded hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* New Folder Modal */}
      {showFolderModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-xl border border-border bg-card p-6 shadow-lg">
            <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <FolderPlus className="h-4 w-4 text-primary" />
              Create New Folder
            </h3>
            <form onSubmit={handleCreateFolder} className="mt-4 flex flex-col gap-4">
              <input
                type="text"
                placeholder="Folder name"
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                required
                className="w-full rounded-md border border-border bg-background px-3 py-1.5 text-xs outline-none focus:border-primary text-foreground"
                autoFocus
              />
              <div className="flex justify-end gap-2 text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => {
                    setShowFolderModal(false);
                    setNewFolderName('');
                  }}
                  className="rounded-md border border-border px-3 py-1.5 text-foreground hover:bg-accent transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreatingFolder}
                  className="rounded-md bg-primary px-3 py-1.5 text-primary-foreground hover:bg-primary/95 transition-colors flex items-center gap-1"
                >
                  {isCreatingFolder && <Loader2 className="h-3 w-3 animate-spin" />}
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
