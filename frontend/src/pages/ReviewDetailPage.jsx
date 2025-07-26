import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Textarea } from '../components/ui/textarea';
import { 
  Star, 
  MapPin, 
  Calendar, 
  ThumbsUp, 
  Share2, 
  Flag,
  Camera,
  Clock,
  DollarSign,
  Users
} from 'lucide-react';

const ReviewDetailPage = () => {
  const { id } = useParams();
  const [newComment, setNewComment] = useState('');
  const [isLiked, setIsLiked] = useState(false);

  // Mock review data
  const review = {
    id: 1,
    title: "Jemaa el-Fnaa Square",
    rating: 4.8,
    category: "Attractions",
    location: {
      name: "Medina, Marrakech",
      address: "Jemaa el-Fnaa, Marrakech 40000, Morocco",
      coordinates: { lat: 31.6259, lng: -7.9891 }
    },
    author: {
      name: "Sarah M.",
      avatar: null,
      reviewCount: 23,
      joinDate: "2023-05-15"
    },
    publishedDate: "2025-01-15",
    visitDate: "2025-01-10",
    content: `
      The heart of Marrakech truly comes alive at Jemaa el-Fnaa Square, especially as the sun begins to set. This UNESCO World Heritage site is an assault on the senses in the most wonderful way possible.

      During the day, the square is relatively calm with a few snake charmers, henna artists, and orange juice vendors. But as evening approaches, it transforms into something magical. Food stalls appear as if by magic, filling the air with the most incredible aromas of grilled meats, tagines, and fresh bread.

      The entertainment is non-stop - storytellers captivate audiences in Arabic and Berber, musicians play traditional instruments, and acrobats perform death-defying stunts. The energy is infectious, and you can't help but get swept up in the atmosphere.

      A few tips for first-time visitors:
      - Come hungry and try the food stalls (they're generally safe and delicious)
      - Negotiate prices for everything, including photos with performers
      - Keep your belongings secure in the crowds
      - Visit both during the day and at night for completely different experiences
      - Don't be afraid to get lost in the surrounding souks

      The square can be overwhelming, but that's part of its charm. It's chaotic, loud, and sometimes pushy, but it's also authentic and unforgettable. This is Morocco at its most vibrant.
    `,
    images: [
      "/api/placeholder/600/400",
      "/api/placeholder/600/400",
      "/api/placeholder/600/400"
    ],
    details: {
      priceRange: "Free to visit",
      bestTimeToVisit: "Sunset (6-8 PM)",
      crowdLevel: "Very Busy",
      accessibility: "Limited"
    },
    likes: 156,
    helpful: 89,
    views: 1247
  };

  const comments = [
    {
      id: 1,
      author: "Ahmed B.",
      content: "Great review! I visited last month and had a similar experience. The food stalls are incredible.",
      date: "2025-01-16",
      likes: 12
    },
    {
      id: 2,
      author: "Maria R.",
      content: "Thanks for the tips! Planning to visit next week and this is very helpful.",
      date: "2025-01-16",
      likes: 8
    }
  ];

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-5 w-5 ${
          i < Math.floor(rating)
            ? 'fill-yellow-400 text-yellow-400'
            : i < rating
            ? 'fill-yellow-200 text-yellow-400'
            : 'text-gray-300'
        }`}
      />
    ));
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Badge variant="secondary">{review.category}</Badge>
            <div className="flex items-center gap-1">
              {renderStars(review.rating)}
              <span className="ml-2 text-lg font-semibold">{review.rating}</span>
            </div>
          </div>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {review.title}
          </h1>
          
          <div className="flex items-center text-gray-600 mb-6">
            <MapPin className="h-5 w-5 mr-2" />
            <span>{review.location.name}</span>
          </div>
          
          {/* Review Meta */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b">
            <div className="flex items-center gap-4">
              <Avatar className="h-12 w-12">
                <AvatarFallback className="bg-orange-100 text-orange-600">
                  {review.author.name.split(' ').map(n => n[0]).join('')}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="font-semibold text-gray-900">{review.author.name}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>{review.author.reviewCount} reviews</span>
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>Visited {new Date(review.visitDate).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button 
                variant={isLiked ? "default" : "outline"} 
                size="sm"
                onClick={() => setIsLiked(!isLiked)}
              >
                <ThumbsUp className="mr-2 h-4 w-4" />
                {isLiked ? 'Liked' : 'Helpful'} ({review.helpful})
              </Button>
              <Button variant="outline" size="sm">
                <Share2 className="mr-2 h-4 w-4" />
                Share
              </Button>
              <Button variant="outline" size="sm">
                <Flag className="mr-2 h-4 w-4" />
                Report
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Images */}
            {review.images && review.images.length > 0 && (
              <Card>
                <CardContent className="p-0">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    <div className="aspect-video bg-gray-200 rounded-tl-lg md:rounded-bl-lg"></div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="aspect-square bg-gray-200"></div>
                      <div className="aspect-square bg-gray-200 rounded-tr-lg relative">
                        <div className="absolute inset-0 bg-black bg-opacity-50 rounded-tr-lg flex items-center justify-center">
                          <div className="text-white text-center">
                            <Camera className="h-6 w-6 mx-auto mb-1" />
                            <span className="text-sm">+{review.images.length - 3} more</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Review Content */}
            <Card>
              <CardContent className="p-6">
                <div className="prose prose-lg max-w-none">
                  {review.content.split('\n\n').map((paragraph, index) => (
                    <p key={index} className="mb-4 text-gray-700 leading-relaxed">
                      {paragraph.trim()}
                    </p>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Comments */}
            <Card>
              <CardHeader>
                <CardTitle>Comments ({comments.length})</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Add Comment */}
                <div className="space-y-3">
                  <Textarea
                    placeholder="Share your thoughts about this review..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    rows={3}
                  />
                  <Button>Post Comment</Button>
                </div>

                {/* Comments List */}
                <div className="space-y-4">
                  {comments.map((comment) => (
                    <div key={comment.id} className="flex gap-3 p-4 bg-gray-50 rounded-lg">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-orange-100 text-orange-600 text-sm">
                          {comment.author.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-sm">{comment.author}</span>
                          <span className="text-xs text-gray-500">
                            {new Date(comment.date).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-gray-700 text-sm mb-2">{comment.content}</p>
                        <Button variant="ghost" size="sm" className="text-xs">
                          <ThumbsUp className="mr-1 h-3 w-3" />
                          {comment.likes}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Info */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Info</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <DollarSign className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="font-medium">Price Range</p>
                    <p className="text-sm text-gray-600">{review.details.priceRange}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="font-medium">Best Time to Visit</p>
                    <p className="text-sm text-gray-600">{review.details.bestTimeToVisit}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  <Users className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="font-medium">Crowd Level</p>
                    <p className="text-sm text-gray-600">{review.details.crowdLevel}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Location */}
            <Card>
              <CardHeader>
                <CardTitle>Location</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="aspect-video bg-gray-200 rounded-lg mb-3"></div>
                <p className="text-sm text-gray-600">{review.location.address}</p>
                <Button variant="outline" size="sm" className="w-full mt-3">
                  Get Directions
                </Button>
              </CardContent>
            </Card>

            {/* Similar Reviews */}
            <Card>
              <CardHeader>
                <CardTitle>Similar Reviews</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { title: "Majorelle Garden", rating: 4.6, category: "Gardens" },
                  { title: "Bahia Palace", rating: 4.5, category: "Historical Sites" }
                ].map((similar, index) => (
                  <div key={index} className="p-3 border rounded-lg hover:shadow-sm transition-shadow cursor-pointer">
                    <h4 className="font-medium text-sm">{similar.title}</h4>
                    <div className="flex items-center justify-between mt-1">
                      <Badge variant="outline" className="text-xs">{similar.category}</Badge>
                      <div className="flex items-center gap-1">
                        <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                        <span className="text-xs">{similar.rating}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReviewDetailPage;

