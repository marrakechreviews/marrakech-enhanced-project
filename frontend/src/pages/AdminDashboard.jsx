import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { 
  Users, 
  FileText, 
  MessageSquare, 
  Settings, 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Search,
  Filter,
  Upload,
  Image,
  BarChart3,
  Calendar,
  Clock,
  Star,
  TrendingUp,
  Activity
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import toast from 'react-hot-toast';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  
  // State for different sections
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalArticles: 0,
    totalReviews: 0,
    totalCategories: 0,
    pendingReviews: 0,
    draftArticles: 0
  });
  
  const [articles, setArticles] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [users, setUsers] = useState([]);
  const [media, setMedia] = useState([]);
  
  // Article form state
  const [articleForm, setArticleForm] = useState({
    title: '',
    content: '',
    excerpt: '',
    category: '',
    tags: '',
    featuredImage: '',
    seo: {
      metaTitle: '',
      metaDescription: '',
      keywords: '',
      canonicalUrl: ''
    }
  });
  
  const [editingArticle, setEditingArticle] = useState(null);
  const [showArticleDialog, setShowArticleDialog] = useState(false);

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/unauthorized');
      return;
    }
    
    fetchDashboardData();
  }, [user, navigate]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch admin stats
      const statsResponse = await api.get('/admin/stats');
      if (statsResponse.data.success) {
        setStats(statsResponse.data.data.overview);
      }
      
      // Fetch articles
      const articlesResponse = await api.get('/articles');
      if (articlesResponse.data.success) {
        setArticles(articlesResponse.data.data);
      }
      
      // Fetch reviews
      const reviewsResponse = await api.get('/reviews');
      if (reviewsResponse.data.success) {
        setReviews(reviewsResponse.data.data);
      }
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateArticle = async () => {
    try {
      const articleData = {
        ...articleForm,
        tags: articleForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };
      
      const response = await api.post('/articles', articleData);
      if (response.data.success) {
        toast.success('Article created successfully');
        setShowArticleDialog(false);
        resetArticleForm();
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Error creating article:', error);
      toast.error('Failed to create article');
    }
  };

  const handleUpdateArticle = async () => {
    try {
      const articleData = {
        ...articleForm,
        tags: articleForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };
      
      const response = await api.put(`/articles/${editingArticle._id}`, articleData);
      if (response.data.success) {
        toast.success('Article updated successfully');
        setShowArticleDialog(false);
        setEditingArticle(null);
        resetArticleForm();
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Error updating article:', error);
      toast.error('Failed to update article');
    }
  };

  const handleDeleteArticle = async (articleId) => {
    try {
      const response = await api.delete(`/articles/${articleId}`);
      if (response.data.success) {
        toast.success('Article deleted successfully');
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Error deleting article:', error);
      toast.error('Failed to delete article');
    }
  };

  const handlePublishArticle = async (articleId) => {
    try {
      const response = await api.put(`/articles/${articleId}/publish`);
      if (response.data.success) {
        toast.success('Article published successfully');
        fetchDashboardData();
      }
    } catch (error) {
      console.error('Error publishing article:', error);
      toast.error('Failed to publish article');
    }
  };

  const resetArticleForm = () => {
    setArticleForm({
      title: '',
      content: '',
      excerpt: '',
      category: '',
      tags: '',
      featuredImage: '',
      seo: {
        metaTitle: '',
        metaDescription: '',
        keywords: '',
        canonicalUrl: ''
      }
    });
  };

  const openEditArticle = (article) => {
    setEditingArticle(article);
    setArticleForm({
      title: article.title || '',
      content: article.content || '',
      excerpt: article.excerpt || '',
      category: article.category || '',
      tags: article.tags ? article.tags.join(', ') : '',
      featuredImage: article.featuredImage || '',
      seo: {
        metaTitle: article.seo?.metaTitle || '',
        metaDescription: article.seo?.metaDescription || '',
        keywords: article.seo?.keywords ? article.seo.keywords.join(', ') : '',
        canonicalUrl: article.seo?.canonicalUrl || ''
      }
    });
    setShowArticleDialog(true);
  };

  const StatCard = ({ title, value, description, icon: Icon, trend }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
        {trend && (
          <div className="flex items-center pt-1">
            <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
            <span className="text-xs text-green-500">{trend}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">Manage your Marrakech Reviews platform</p>
        </div>
        <Button onClick={logout} variant="outline">
          Logout
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="articles">Articles</TabsTrigger>
          <TabsTrigger value="reviews">Reviews</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="media">Media</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Users"
              value={stats.totalUsers}
              description="Registered users"
              icon={Users}
              trend="+12% from last month"
            />
            <StatCard
              title="Total Articles"
              value={stats.totalArticles}
              description="Published articles"
              icon={FileText}
              trend="+8% from last month"
            />
            <StatCard
              title="Total Reviews"
              value={stats.totalReviews}
              description="User reviews"
              icon={MessageSquare}
              trend="+15% from last month"
            />
            <StatCard
              title="Pending Reviews"
              value={stats.pendingReviews}
              description="Awaiting moderation"
              icon={Clock}
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest actions on your platform</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <Activity className="h-4 w-4 text-blue-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">New article published</p>
                      <p className="text-xs text-muted-foreground">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <Users className="h-4 w-4 text-green-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">New user registered</p>
                      <p className="text-xs text-muted-foreground">4 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <MessageSquare className="h-4 w-4 text-orange-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Review pending approval</p>
                      <p className="text-xs text-muted-foreground">6 hours ago</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Common administrative tasks</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={() => {
                    setActiveTab('articles');
                    setShowArticleDialog(true);
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create New Article
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={() => setActiveTab('reviews')}
                >
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Review Pending Content
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={() => setActiveTab('users')}
                >
                  <Users className="mr-2 h-4 w-4" />
                  Manage Users
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={() => setActiveTab('media')}
                >
                  <Image className="mr-2 h-4 w-4" />
                  Media Library
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="articles" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Articles Management</h2>
            <Dialog open={showArticleDialog} onOpenChange={setShowArticleDialog}>
              <DialogTrigger asChild>
                <Button onClick={() => {
                  resetArticleForm();
                  setEditingArticle(null);
                }}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Article
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>
                    {editingArticle ? 'Edit Article' : 'Create New Article'}
                  </DialogTitle>
                  <DialogDescription>
                    {editingArticle ? 'Update the article details below.' : 'Fill in the details to create a new article.'}
                  </DialogDescription>
                </DialogHeader>
                
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      value={articleForm.title}
                      onChange={(e) => setArticleForm({...articleForm, title: e.target.value})}
                      placeholder="Enter article title"
                    />
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="excerpt">Excerpt</Label>
                    <Textarea
                      id="excerpt"
                      value={articleForm.excerpt}
                      onChange={(e) => setArticleForm({...articleForm, excerpt: e.target.value})}
                      placeholder="Brief description of the article"
                      rows={3}
                    />
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="content">Content</Label>
                    <Textarea
                      id="content"
                      value={articleForm.content}
                      onChange={(e) => setArticleForm({...articleForm, content: e.target.value})}
                      placeholder="Article content (supports HTML)"
                      rows={10}
                      className="font-mono text-sm"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="category">Category</Label>
                      <Select 
                        value={articleForm.category} 
                        onValueChange={(value) => setArticleForm({...articleForm, category: value})}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="restaurants">Restaurants</SelectItem>
                          <SelectItem value="hotels">Hotels & Riads</SelectItem>
                          <SelectItem value="attractions">Attractions</SelectItem>
                          <SelectItem value="shopping">Shopping</SelectItem>
                          <SelectItem value="activities">Activities</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="grid gap-2">
                      <Label htmlFor="tags">Tags</Label>
                      <Input
                        id="tags"
                        value={articleForm.tags}
                        onChange={(e) => setArticleForm({...articleForm, tags: e.target.value})}
                        placeholder="tag1, tag2, tag3"
                      />
                    </div>
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="featuredImage">Featured Image URL</Label>
                    <Input
                      id="featuredImage"
                      value={articleForm.featuredImage}
                      onChange={(e) => setArticleForm({...articleForm, featuredImage: e.target.value})}
                      placeholder="https://example.com/image.jpg"
                    />
                  </div>
                  
                  <div className="border-t pt-4">
                    <h4 className="text-lg font-semibold mb-4">SEO Settings</h4>
                    <div className="grid gap-4">
                      <div className="grid gap-2">
                        <Label htmlFor="metaTitle">Meta Title</Label>
                        <Input
                          id="metaTitle"
                          value={articleForm.seo.metaTitle}
                          onChange={(e) => setArticleForm({
                            ...articleForm, 
                            seo: {...articleForm.seo, metaTitle: e.target.value}
                          })}
                          placeholder="SEO title (60 characters max)"
                        />
                      </div>
                      
                      <div className="grid gap-2">
                        <Label htmlFor="metaDescription">Meta Description</Label>
                        <Textarea
                          id="metaDescription"
                          value={articleForm.seo.metaDescription}
                          onChange={(e) => setArticleForm({
                            ...articleForm, 
                            seo: {...articleForm.seo, metaDescription: e.target.value}
                          })}
                          placeholder="SEO description (160 characters max)"
                          rows={3}
                        />
                      </div>
                      
                      <div className="grid gap-2">
                        <Label htmlFor="keywords">Keywords</Label>
                        <Input
                          id="keywords"
                          value={articleForm.seo.keywords}
                          onChange={(e) => setArticleForm({
                            ...articleForm, 
                            seo: {...articleForm.seo, keywords: e.target.value}
                          })}
                          placeholder="keyword1, keyword2, keyword3"
                        />
                      </div>
                      
                      <div className="grid gap-2">
                        <Label htmlFor="canonicalUrl">Canonical URL</Label>
                        <Input
                          id="canonicalUrl"
                          value={articleForm.seo.canonicalUrl}
                          onChange={(e) => setArticleForm({
                            ...articleForm, 
                            seo: {...articleForm.seo, canonicalUrl: e.target.value}
                          })}
                          placeholder="https://example.com/canonical-url"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowArticleDialog(false)}>
                    Cancel
                  </Button>
                  <Button onClick={editingArticle ? handleUpdateArticle : handleCreateArticle}>
                    {editingArticle ? 'Update Article' : 'Create Article'}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>All Articles</CardTitle>
              <CardDescription>Manage your published and draft articles</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Views</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {articles.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8">
                        <div className="flex flex-col items-center space-y-2">
                          <FileText className="h-8 w-8 text-muted-foreground" />
                          <p className="text-muted-foreground">No articles found</p>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => setShowArticleDialog(true)}
                          >
                            Create your first article
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    articles.map((article) => (
                      <TableRow key={article._id}>
                        <TableCell className="font-medium">{article.title}</TableCell>
                        <TableCell>
                          <Badge variant="secondary">{article.category}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={article.status === 'published' ? 'default' : 'secondary'}
                          >
                            {article.status}
                          </Badge>
                        </TableCell>
                        <TableCell>{article.views || 0}</TableCell>
                        <TableCell>
                          {new Date(article.createdAt).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => openEditArticle(article)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            {article.status === 'draft' && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handlePublishArticle(article._id)}
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            )}
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <Button variant="outline" size="sm">
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Delete Article</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    Are you sure you want to delete "{article.title}"? This action cannot be undone.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                                  <AlertDialogAction 
                                    onClick={() => handleDeleteArticle(article._id)}
                                    className="bg-red-600 hover:bg-red-700"
                                  >
                                    Delete
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reviews" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Reviews Management</h2>
            <div className="flex space-x-2">
              <Button variant="outline">
                <Filter className="mr-2 h-4 w-4" />
                Filter
              </Button>
              <Button variant="outline">
                <Search className="mr-2 h-4 w-4" />
                Search
              </Button>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>All Reviews</CardTitle>
              <CardDescription>Moderate and manage user reviews</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Rating</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reviews.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8">
                        <div className="flex flex-col items-center space-y-2">
                          <MessageSquare className="h-8 w-8 text-muted-foreground" />
                          <p className="text-muted-foreground">No reviews found</p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    reviews.map((review) => (
                      <TableRow key={review._id}>
                        <TableCell>{review.author?.username || 'Anonymous'}</TableCell>
                        <TableCell>{review.location?.name || 'N/A'}</TableCell>
                        <TableCell>
                          <div className="flex items-center">
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400 mr-1" />
                            {review.rating}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={review.status === 'approved' ? 'default' : 'secondary'}
                          >
                            {review.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {new Date(review.createdAt).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="outline" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button variant="outline" size="sm">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">User Management</h2>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add User
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>All Users</CardTitle>
              <CardDescription>Manage user accounts and permissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Users className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">User management interface coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="media" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Media Library</h2>
            <Button>
              <Upload className="mr-2 h-4 w-4" />
              Upload Media
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Media Files</CardTitle>
              <CardDescription>Manage your media assets</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Image className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">Media library interface coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Settings</h2>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Platform Settings</CardTitle>
              <CardDescription>Configure your platform settings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Settings className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">Settings interface coming soon</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminDashboard;

