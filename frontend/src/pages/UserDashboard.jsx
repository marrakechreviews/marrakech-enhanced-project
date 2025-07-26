import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  User, 
  Star, 
  Gift, 
  MessageSquare, 
  Calendar, 
  MapPin,
  Edit,
  Trash2,
  Plus,
  Copy,
  Clock,
  Award,
  TrendingUp,
  Heart,
  Eye,
  CheckCircle,
  AlertCircle,
  Ticket
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from "@/lib/api";
import toast from 'react-hot-toast';

const UserDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  
  // User stats
  const [userStats, setUserStats] = useState({
    totalReviews: 0,
    totalLikes: 0,
    totalViews: 0,
    memberSince: null,
    couponsUsed: 0,
    totalSavings: 0
  });
  
  // Reviews
  const [userReviews, setUserReviews] = useState([]);
  const [showAddReviewDialog, setShowAddReviewDialog] = useState(false);
  const [editingReview, setEditingReview] = useState(null);
  const [reviewForm, setReviewForm] = useState({
    title: '',
    content: '',
    rating: 5,
    location: '',
    category: 'restaurant'
  });
  
  // Coupons
  const [availableCoupons, setAvailableCoupons] = useState([]);
  const [usedCoupons, setUsedCoupons] = useState([]);
  const [weeklyCouponClaimed, setWeeklyCouponClaimed] = useState(false);
  const [couponStats, setCouponStats] = useState({
    totalUsed: 0,
    totalSaved: 0,
    lastUsed: null
  });

  useEffect(() => {
    fetchUserStats();
    fetchUserReviews();
    fetchUserCoupons();
    fetchCouponStats();
    checkWeeklyCoupon();
  }, []);

  const fetchUserStats = async () => {
    try {
      const response = await api.get('/users/stats');
      if (response.data.success) {
        setUserStats(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching user stats:', error);
    }
  };

  const fetchUserReviews = async () => {
    try {
      const response = await api.get('/reviews/my-reviews');
      if (response.data.success) {
        setUserReviews(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching user reviews:', error);
    }
  };

  const fetchUserCoupons = async () => {
    try {
      const response = await api.get('/coupons');
      if (response.data.success) {
        setAvailableCoupons(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching coupons:', error);
    }
  };

  const fetchCouponStats = async () => {
    try {
      const response = await api.get('/coupons/my-usage');
      if (response.data.success) {
        setCouponStats(response.data.data);
      }
    } catch (error) {
      console.error('Error fetching coupon stats:', error);
    }
  };

  const checkWeeklyCoupon = async () => {
    // Check if user has already claimed weekly coupon
    const weekStart = new Date();
    weekStart.setDate(weekStart.getDate() - weekStart.getDay());
    weekStart.setHours(0, 0, 0, 0);
    
    try {
      const response = await api.get('/coupons');
      if (response.data.success) {
        const weeklyCoupon = response.data.data.find(coupon => 
          coupon.type === 'weekly_reward' && 
          new Date(coupon.createdAt) >= weekStart
        );
        setWeeklyCouponClaimed(!!weeklyCoupon);
      }
    } catch (error) {
      console.error('Error checking weekly coupon:', error);
    }
  };

  const handleClaimWeeklyCoupon = async () => {
    try {
      const response = await api.post('/coupons/weekly');
      if (response.data.success) {
        toast.success('Weekly coupon claimed successfully!');
        setWeeklyCouponClaimed(true);
        fetchUserCoupons();
      }
    } catch (error) {
      if (error.response?.status === 409) {
        toast.error('You have already claimed your weekly coupon');
        setWeeklyCouponClaimed(true);
      } else {
        toast.error('Failed to claim weekly coupon');
      }
    }
  };

  const handleAddReview = async () => {
    try {
      const response = await api.post('/reviews', reviewForm);
      if (response.data.success) {
        toast.success('Review added successfully!');
        setShowAddReviewDialog(false);
        setReviewForm({
          title: '',
          content: '',
          rating: 5,
          location: '',
          category: 'restaurant'
        });
        fetchUserReviews();
        fetchUserStats();
      }
    } catch (error) {
      toast.error('Failed to add review');
    }
  };

  const handleEditReview = async () => {
    if (!editingReview) return;
    
    try {
      const response = await api.put(`/reviews/${editingReview._id}`, reviewForm);
      if (response.data.success) {
        toast.success('Review updated successfully!');
        setEditingReview(null);
        fetchUserReviews();
      }
    } catch (error) {
      toast.error('Failed to update review');
    }
  };

  const handleDeleteReview = async (reviewId) => {
    try {
      const response = await api.delete(`/reviews/${reviewId}`);
      if (response.data.success) {
        toast.success('Review deleted successfully!');
        fetchUserReviews();
        fetchUserStats();
      }
    } catch (error) {
      toast.error('Failed to delete review');
    }
  };

  const openEditDialog = (review) => {
    setEditingReview(review);
    setReviewForm({
      title: review.title,
      content: review.content,
      rating: review.rating,
      location: review.location,
      category: review.category
    });
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Coupon code copied to clipboard!');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.firstName}!</h1>
          <p className="text-muted-foreground">Manage your reviews and claim your rewards</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="secondary" className="text-sm">
            <User className="mr-1 h-3 w-3" />
            Member since {userStats.memberSince ? formatDate(userStats.memberSince) : 'Recently'}
          </Badge>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Reviews</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{userStats.totalReviews}</div>
            <p className="text-xs text-muted-foreground">
              +2 from last month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Likes</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{userStats.totalLikes}</div>
            <p className="text-xs text-muted-foreground">
              +12 from last week
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Profile Views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{userStats.totalViews}</div>
            <p className="text-xs text-muted-foreground">
              +5% from last month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Savings</CardTitle>
            <Gift className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${couponStats.totalSaved}</div>
            <p className="text-xs text-muted-foreground">
              From {couponStats.totalUsed} coupons used
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="reviews" className="space-y-4">
        <TabsList>
          <TabsTrigger value="reviews">My Reviews</TabsTrigger>
          <TabsTrigger value="coupons">Coupons & Rewards</TabsTrigger>
          <TabsTrigger value="profile">Profile Settings</TabsTrigger>
        </TabsList>
        
        <TabsContent value="reviews" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">My Reviews</h2>
            <Dialog open={showAddReviewDialog} onOpenChange={setShowAddReviewDialog}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Review
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Add New Review</DialogTitle>
                  <DialogDescription>
                    Share your experience and help other travelers discover great places in Marrakech
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="title">Review Title</Label>
                    <Input
                      id="title"
                      value={reviewForm.title}
                      onChange={(e) => setReviewForm({...reviewForm, title: e.target.value})}
                      placeholder="Give your review a catchy title"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="location">Location</Label>
                      <Input
                        id="location"
                        value={reviewForm.location}
                        onChange={(e) => setReviewForm({...reviewForm, location: e.target.value})}
                        placeholder="Restaurant/Place name"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="category">Category</Label>
                      <Select value={reviewForm.category} onValueChange={(value) => setReviewForm({...reviewForm, category: value})}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="restaurant">Restaurant</SelectItem>
                          <SelectItem value="hotel">Hotel</SelectItem>
                          <SelectItem value="attraction">Attraction</SelectItem>
                          <SelectItem value="shopping">Shopping</SelectItem>
                          <SelectItem value="activity">Activity</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="grid gap-2">
                    <Label>Rating</Label>
                    <div className="flex space-x-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Button
                          key={star}
                          variant="ghost"
                          size="sm"
                          onClick={() => setReviewForm({...reviewForm, rating: star})}
                        >
                          <Star
                            className={`h-6 w-6 ${star <= reviewForm.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                          />
                        </Button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid gap-2">
                    <Label htmlFor="content">Review Content</Label>
                    <Textarea
                      id="content"
                      value={reviewForm.content}
                      onChange={(e) => setReviewForm({...reviewForm, content: e.target.value})}
                      placeholder="Share your detailed experience..."
                      rows={6}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowAddReviewDialog(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleAddReview}>
                    Publish Review
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
          
          {userReviews.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No reviews yet</h3>
                <p className="text-gray-500 mb-4">Share your first experience to help other travelers</p>
                <Button onClick={() => setShowAddReviewDialog(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Write Your First Review
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {userReviews.map((review) => (
                <Card key={review._id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-xl">{review.title}</CardTitle>
                        <div className="flex items-center space-x-4 mt-2">
                          <div className="flex">{renderStars(review.rating)}</div>
                          <Badge variant="secondary">{review.category}</Badge>
                          <span className="text-sm text-gray-500 flex items-center">
                            <MapPin className="h-3 w-3 mr-1" />
                            {review.location}
                          </span>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button variant="ghost" size="sm" onClick={() => openEditDialog(review)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Delete Review</AlertDialogTitle>
                              <AlertDialogDescription>
                                Are you sure you want to delete this review? This action cannot be undone.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction 
                                onClick={() => handleDeleteReview(review._id)}
                                className="bg-red-600 hover:bg-red-700"
                              >
                                Delete
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 mb-4">{review.content}</p>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(review.createdAt)}
                      </span>
                      <div className="flex items-center space-x-4">
                        <span className="flex items-center">
                          <Heart className="h-3 w-3 mr-1" />
                          {review.likes || 0} likes
                        </span>
                        <span className="flex items-center">
                          <Eye className="h-3 w-3 mr-1" />
                          {review.views || 0} views
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="coupons" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Coupons & Rewards</h2>
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="text-sm">
                <Gift className="mr-1 h-3 w-3" />
                ${couponStats.totalSaved} saved
              </Badge>
            </div>
          </div>
          
          {/* Weekly Coupon Claim */}
          <Card className="border-orange-200 bg-orange-50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl text-orange-800">Weekly Reward</CardTitle>
                  <CardDescription className="text-orange-600">
                    Claim your free 10% discount coupon every week
                  </CardDescription>
                </div>
                <div className="text-right">
                  {weeklyCouponClaimed ? (
                    <Badge className="bg-green-500 hover:bg-green-600">
                      <CheckCircle className="mr-1 h-3 w-3" />
                      Claimed
                    </Badge>
                  ) : (
                    <Button onClick={handleClaimWeeklyCoupon} className="bg-orange-600 hover:bg-orange-700">
                      <Gift className="mr-2 h-4 w-4" />
                      Claim Now
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            {weeklyCouponClaimed && (
              <CardContent>
                <div className="flex items-center text-sm text-orange-700">
                  <Clock className="h-4 w-4 mr-2" />
                  Next coupon available in {7 - new Date().getDay()} days
                </div>
              </CardContent>
            )}
          </Card>
          
          {/* Available Coupons */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Available Coupons</h3>
            {availableCoupons.length === 0 ? (
              <Card>
                <CardContent className="text-center py-8">
                  <Ticket className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">No coupons available</h3>
                  <p className="text-gray-500">Check back later for new offers</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid md:grid-cols-2 gap-4">
                {availableCoupons.map((coupon) => (
                  <Card key={coupon._id} className="border-green-200 bg-green-50">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg text-green-800">{coupon.title}</CardTitle>
                          <CardDescription className="text-green-600">
                            {coupon.description}
                          </CardDescription>
                        </div>
                        <Badge className="bg-green-500 hover:bg-green-600">
                          {coupon.valueType === 'percentage' ? `${coupon.value}%` : `$${coupon.value}`} OFF
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">Code:</span>
                          <div className="flex items-center space-x-2">
                            <code className="bg-white px-2 py-1 rounded text-sm font-mono">
                              {coupon.code}
                            </code>
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => copyToClipboard(coupon.code)}
                            >
                              <Copy className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        
                        <div className="text-sm text-green-700 space-y-1">
                          <div className="flex justify-between">
                            <span>Valid until:</span>
                            <span>{formatDate(coupon.validUntil)}</span>
                          </div>
                          {coupon.minOrderAmount > 0 && (
                            <div className="flex justify-between">
                              <span>Min. order:</span>
                              <span>${coupon.minOrderAmount}</span>
                            </div>
                          )}
                          <div className="flex justify-between">
                            <span>Uses left:</span>
                            <span>{coupon.usageLimit - coupon.usageCount}</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="profile" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>
                Update your personal information and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="firstName">First Name</Label>
                  <Input id="firstName" defaultValue={user?.firstName} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input id="lastName" defaultValue={user?.lastName} />
                </div>
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" defaultValue={user?.email} />
              </div>
              
              <div className="grid gap-2">
                <Label htmlFor="bio">Bio</Label>
                <Textarea 
                  id="bio" 
                  placeholder="Tell us about yourself..."
                  rows={3}
                />
              </div>
              
              <Button>Save Changes</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Edit Review Dialog */}
      <Dialog open={!!editingReview} onOpenChange={() => setEditingReview(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Review</DialogTitle>
            <DialogDescription>
              Update your review to reflect your latest thoughts
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="editTitle">Review Title</Label>
              <Input
                id="editTitle"
                value={reviewForm.title}
                onChange={(e) => setReviewForm({...reviewForm, title: e.target.value})}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="editLocation">Location</Label>
                <Input
                  id="editLocation"
                  value={reviewForm.location}
                  onChange={(e) => setReviewForm({...reviewForm, location: e.target.value})}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="editCategory">Category</Label>
                <Select value={reviewForm.category} onValueChange={(value) => setReviewForm({...reviewForm, category: value})}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="restaurant">Restaurant</SelectItem>
                    <SelectItem value="hotel">Hotel</SelectItem>
                    <SelectItem value="attraction">Attraction</SelectItem>
                    <SelectItem value="shopping">Shopping</SelectItem>
                    <SelectItem value="activity">Activity</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="grid gap-2">
              <Label>Rating</Label>
              <div className="flex space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Button
                    key={star}
                    variant="ghost"
                    size="sm"
                    onClick={() => setReviewForm({...reviewForm, rating: star})}
                  >
                    <Star
                      className={`h-6 w-6 ${star <= reviewForm.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                    />
                  </Button>
                ))}
              </div>
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="editContent">Review Content</Label>
              <Textarea
                id="editContent"
                value={reviewForm.content}
                onChange={(e) => setReviewForm({...reviewForm, content: e.target.value})}
                rows={6}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingReview(null)}>
              Cancel
            </Button>
            <Button onClick={handleEditReview}>
              Update Review
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserDashboard;

