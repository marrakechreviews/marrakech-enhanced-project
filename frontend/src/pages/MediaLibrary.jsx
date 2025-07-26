import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Upload, 
  Image, 
  Video, 
  FileText, 
  Folder, 
  FolderPlus,
  Search,
  Filter,
  Grid3X3,
  List,
  Trash2,
  Edit,
  Download,
  Eye,
  Copy,
  Move,
  Tag,
  Calendar,
  User,
  HardDrive,
  MoreHorizontal
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import toast from 'react-hot-toast';

const MediaLibrary = () => {
  const { user } = useAuth();
  const fileInputRef = useRef(null);
  
  const [media, setMedia] = useState([]);
  const [folders, setFolders] = useState([]);
  const [selectedMedia, setSelectedMedia] = useState([]);
  const [currentFolder, setCurrentFolder] = useState('uploads');
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  // Filters and search
  const [searchTerm, setSearchTerm] = useState('');
  const [fileTypeFilter, setFileTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('createdAt');
  const [sortOrder, setSortOrder] = useState('desc');
  
  // Dialogs
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showCreateFolderDialog, setShowCreateFolderDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showMoveDialog, setShowMoveDialog] = useState(false);
  
  // Forms
  const [newFolderName, setNewFolderName] = useState('');
  const [editingMedia, setEditingMedia] = useState(null);
  const [editForm, setEditForm] = useState({
    alt: '',
    caption: '',
    tags: ''
  });
  
  // Stats
  const [stats, setStats] = useState({
    totalFiles: 0,
    totalSize: 0,
    typeDistribution: []
  });

  useEffect(() => {
    fetchMedia();
    fetchFolders();
    fetchStats();
  }, [currentFolder, fileTypeFilter, searchTerm, sortBy, sortOrder]);

  const fetchMedia = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        folder: currentFolder,
        ...(fileTypeFilter !== 'all' && { type: fileTypeFilter }),
        ...(searchTerm && { search: searchTerm }),
        sort: sortBy,
        order: sortOrder,
        limit: '50'
      });
      
      const response = await api.get(`/media?${params}`);
      if (response.data.success) {
        setMedia(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching media:', error);
      toast.error('Failed to load media');
    } finally {
      setLoading(false);
    }
  };

  const fetchFolders = async () => {
    try {
      const response = await api.get('/media/folders');
      if (response.data.success) {
        setFolders(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching folders:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/media/stats');
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    
    setUploading(true);
    const uploadPromises = Array.from(files).map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('folder', currentFolder);
      
      try {
        const response = await api.post('/media/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        if (response.data.success) {
          toast.success(`${file.name} uploaded successfully`);
          return response.data.data;
        }
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
        toast.error(`Failed to upload ${file.name}`);
        return null;
      }
    });
    
    try {
      await Promise.all(uploadPromises);
      fetchMedia();
      fetchStats();
      setShowUploadDialog(false);
    } finally {
      setUploading(false);
    }
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) return;
    
    try {
      const response = await api.post('/media/folders', {
        name: newFolderName.trim()
      });
      
      if (response.data.success) {
        toast.success('Folder created successfully');
        setNewFolderName('');
        setShowCreateFolderDialog(false);
        fetchFolders();
      }
    } catch (error) {
      console.error('Error creating folder:', error);
      toast.error('Failed to create folder');
    }
  };

  const handleEditMedia = async () => {
    if (!editingMedia) return;
    
    try {
      const updateData = {
        alt: editForm.alt,
        caption: editForm.caption,
        tags: editForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };
      
      const response = await api.put(`/media/${editingMedia._id}`, updateData);
      
      if (response.data.success) {
        toast.success('Media updated successfully');
        setShowEditDialog(false);
        setEditingMedia(null);
        fetchMedia();
      }
    } catch (error) {
      console.error('Error updating media:', error);
      toast.error('Failed to update media');
    }
  };

  const handleDeleteMedia = async (mediaIds) => {
    try {
      const deletePromises = mediaIds.map(id => api.delete(`/media/${id}`));
      await Promise.all(deletePromises);
      
      toast.success(`${mediaIds.length} file(s) deleted successfully`);
      setSelectedMedia([]);
      fetchMedia();
      fetchStats();
    } catch (error) {
      console.error('Error deleting media:', error);
      toast.error('Failed to delete media');
    }
  };

  const handleMoveMedia = async (targetFolder) => {
    if (selectedMedia.length === 0) return;
    
    try {
      const response = await api.post('/media/bulk/move', {
        media_ids: selectedMedia,
        folder: targetFolder
      });
      
      if (response.data.success) {
        toast.success(`${selectedMedia.length} file(s) moved successfully`);
        setSelectedMedia([]);
        setShowMoveDialog(false);
        fetchMedia();
      }
    } catch (error) {
      console.error('Error moving media:', error);
      toast.error('Failed to move media');
    }
  };

  const openEditDialog = (mediaItem) => {
    setEditingMedia(mediaItem);
    setEditForm({
      alt: mediaItem.alt || '',
      caption: mediaItem.caption || '',
      tags: mediaItem.tags ? mediaItem.tags.join(', ') : ''
    });
    setShowEditDialog(true);
  };

  const copyToClipboard = (url) => {
    navigator.clipboard.writeText(url);
    toast.success('URL copied to clipboard');
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (mimeType) => {
    if (mimeType.startsWith('image/')) return <Image className="h-4 w-4" />;
    if (mimeType.startsWith('video/')) return <Video className="h-4 w-4" />;
    return <FileText className="h-4 w-4" />;
  };

  const MediaCard = ({ item }) => (
    <Card className={`cursor-pointer transition-all hover:shadow-md ${selectedMedia.includes(item._id) ? 'ring-2 ring-blue-500' : ''}`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <Checkbox
            checked={selectedMedia.includes(item._id)}
            onCheckedChange={(checked) => {
              if (checked) {
                setSelectedMedia([...selectedMedia, item._id]);
              } else {
                setSelectedMedia(selectedMedia.filter(id => id !== item._id));
              }
            }}
          />
          <div className="flex space-x-1">
            <Button variant="ghost" size="sm" onClick={() => copyToClipboard(item.url)}>
              <Copy className="h-3 w-3" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => openEditDialog(item)}>
              <Edit className="h-3 w-3" />
            </Button>
          </div>
        </div>
        
        <div className="aspect-square bg-gray-100 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
          {item.mimeType.startsWith('image/') ? (
            <img 
              src={item.url} 
              alt={item.alt || item.originalName}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="flex flex-col items-center text-gray-500">
              {getFileIcon(item.mimeType)}
              <span className="text-xs mt-1">{item.mimeType.split('/')[1].toUpperCase()}</span>
            </div>
          )}
        </div>
        
        <div className="space-y-1">
          <p className="text-sm font-medium truncate" title={item.originalName}>
            {item.originalName}
          </p>
          <p className="text-xs text-gray-500">{formatFileSize(item.size)}</p>
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>{new Date(item.createdAt).toLocaleDateString()}</span>
            {item.tags && item.tags.length > 0 && (
              <Badge variant="secondary" className="text-xs">
                <Tag className="h-2 w-2 mr-1" />
                {item.tags.length}
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const MediaListItem = ({ item }) => (
    <div className={`flex items-center p-3 border rounded-lg ${selectedMedia.includes(item._id) ? 'bg-blue-50 border-blue-200' : 'hover:bg-gray-50'}`}>
      <Checkbox
        checked={selectedMedia.includes(item._id)}
        onCheckedChange={(checked) => {
          if (checked) {
            setSelectedMedia([...selectedMedia, item._id]);
          } else {
            setSelectedMedia(selectedMedia.filter(id => id !== item._id));
          }
        }}
        className="mr-3"
      />
      
      <div className="w-12 h-12 bg-gray-100 rounded flex items-center justify-center mr-3">
        {item.mimeType.startsWith('image/') ? (
          <img 
            src={item.url} 
            alt={item.alt || item.originalName}
            className="w-full h-full object-cover rounded"
          />
        ) : (
          getFileIcon(item.mimeType)
        )}
      </div>
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{item.originalName}</p>
        <p className="text-xs text-gray-500">{formatFileSize(item.size)} • {new Date(item.createdAt).toLocaleDateString()}</p>
      </div>
      
      <div className="flex items-center space-x-2">
        {item.tags && item.tags.length > 0 && (
          <Badge variant="secondary" className="text-xs">
            <Tag className="h-2 w-2 mr-1" />
            {item.tags.length}
          </Badge>
        )}
        <Button variant="ghost" size="sm" onClick={() => copyToClipboard(item.url)}>
          <Copy className="h-3 w-3" />
        </Button>
        <Button variant="ghost" size="sm" onClick={() => openEditDialog(item)}>
          <Edit className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Media Library</h1>
          <p className="text-muted-foreground">Manage your media assets</p>
        </div>
        
        <div className="flex space-x-2">
          <Dialog open={showCreateFolderDialog} onOpenChange={setShowCreateFolderDialog}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <FolderPlus className="mr-2 h-4 w-4" />
                New Folder
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Folder</DialogTitle>
                <DialogDescription>
                  Enter a name for the new folder
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="folderName">Folder Name</Label>
                  <Input
                    id="folderName"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                    placeholder="Enter folder name"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowCreateFolderDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateFolder}>
                  Create Folder
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
          
          <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
            <DialogTrigger asChild>
              <Button>
                <Upload className="mr-2 h-4 w-4" />
                Upload Files
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload Files</DialogTitle>
                <DialogDescription>
                  Select files to upload to the current folder: {currentFolder}
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div 
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-gray-400 transition-colors"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-lg font-medium">Click to upload files</p>
                  <p className="text-sm text-gray-500">or drag and drop files here</p>
                  <p className="text-xs text-gray-400 mt-2">
                    Supports: PNG, JPG, GIF, WebP, SVG, MP4, MOV, PDF, DOC
                  </p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*,video/*,.pdf,.doc,.docx"
                  onChange={(e) => handleFileUpload(e.target.files)}
                  className="hidden"
                />
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowUploadDialog(false)}>
                  Cancel
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Files</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalFiles}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatFileSize(stats.totalSize)}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current Folder</CardTitle>
            <Folder className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{currentFolder}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Selected</CardTitle>
            <Checkbox className="h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{selectedMedia.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex flex-wrap gap-2">
          <Select value={currentFolder} onValueChange={setCurrentFolder}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="uploads">uploads</SelectItem>
              {folders.map(folder => (
                <SelectItem key={folder} value={folder}>{folder}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select value={fileTypeFilter} onValueChange={setFileTypeFilter}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="image">Images</SelectItem>
              <SelectItem value="video">Videos</SelectItem>
              <SelectItem value="document">Documents</SelectItem>
            </SelectContent>
          </Select>
          
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search media..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-64"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {selectedMedia.length > 0 && (
            <>
              <Dialog open={showMoveDialog} onOpenChange={setShowMoveDialog}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Move className="mr-2 h-4 w-4" />
                    Move ({selectedMedia.length})
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Move Files</DialogTitle>
                    <DialogDescription>
                      Select the destination folder for {selectedMedia.length} selected file(s)
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <Select onValueChange={handleMoveMedia}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select destination folder" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="uploads">uploads</SelectItem>
                        {folders.filter(f => f !== currentFolder).map(folder => (
                          <SelectItem key={folder} value={folder}>{folder}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </DialogContent>
              </Dialog>
              
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete ({selectedMedia.length})
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Delete Files</AlertDialogTitle>
                    <AlertDialogDescription>
                      Are you sure you want to delete {selectedMedia.length} selected file(s)? This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction 
                      onClick={() => handleDeleteMedia(selectedMedia)}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      Delete
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </>
          )}
          
          <div className="flex border rounded-lg">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Media Grid/List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : media.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Image className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No media files found</h3>
            <p className="text-gray-500 mb-4">Upload your first file to get started</p>
            <Button onClick={() => setShowUploadDialog(true)}>
              <Upload className="mr-2 h-4 w-4" />
              Upload Files
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className={viewMode === 'grid' 
          ? "grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4" 
          : "space-y-2"
        }>
          {media.map((item) => (
            viewMode === 'grid' 
              ? <MediaCard key={item._id} item={item} />
              : <MediaListItem key={item._id} item={item} />
          ))}
        </div>
      )}

      {/* Edit Media Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Media</DialogTitle>
            <DialogDescription>
              Update the metadata for this media file
            </DialogDescription>
          </DialogHeader>
          {editingMedia && (
            <div className="grid gap-4 py-4">
              <div className="flex justify-center">
                {editingMedia.mimeType.startsWith('image/') ? (
                  <img 
                    src={editingMedia.url} 
                    alt={editingMedia.alt || editingMedia.originalName}
                    className="max-w-48 max-h-48 object-contain rounded"
                  />
                ) : (
                  <div className="w-48 h-48 bg-gray-100 rounded flex items-center justify-center">
                    {getFileIcon(editingMedia.mimeType)}
                  </div>
                )}
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="alt">Alt Text</Label>
                <Input
                  id="alt"
                  value={editForm.alt}
                  onChange={(e) => setEditForm({...editForm, alt: e.target.value})}
                  placeholder="Describe this image for accessibility"
                />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="caption">Caption</Label>
                <Textarea
                  id="caption"
                  value={editForm.caption}
                  onChange={(e) => setEditForm({...editForm, caption: e.target.value})}
                  placeholder="Add a caption for this media"
                  rows={3}
                />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="tags">Tags</Label>
                <Input
                  id="tags"
                  value={editForm.tags}
                  onChange={(e) => setEditForm({...editForm, tags: e.target.value})}
                  placeholder="tag1, tag2, tag3"
                />
              </div>
              
              <div className="text-sm text-gray-500 space-y-1">
                <p><strong>File:</strong> {editingMedia.originalName}</p>
                <p><strong>Size:</strong> {formatFileSize(editingMedia.size)}</p>
                <p><strong>Type:</strong> {editingMedia.mimeType}</p>
                <p><strong>URL:</strong> 
                  <Button 
                    variant="link" 
                    className="p-0 h-auto text-blue-600"
                    onClick={() => copyToClipboard(editingMedia.url)}
                  >
                    Copy URL
                  </Button>
                </p>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleEditMedia}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MediaLibrary;

