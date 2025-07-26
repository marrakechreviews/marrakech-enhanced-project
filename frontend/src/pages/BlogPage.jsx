import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Search, 
  Calendar, 
  User, 
  Clock, 
  Eye,
  Heart,
  MessageCircle,
  ArrowRight,
  TrendingUp,
  BookOpen,
  Tag
} from 'lucide-react';

const BlogPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('latest');

  // Sample blog data - in real app, this would come from API
  const blogPosts = [
    {
      id: 1,
      title: '10 Hidden Gems in Marrakech\'s Medina You Must Visit',
      excerpt: 'Discover the secret corners of Marrakech\'s ancient medina that most tourists never see. From hidden gardens to artisan workshops, these gems offer authentic experiences.',
      content: 'Full article content would go here...',
      author: 'Youssef Benali',
      authorAvatar: '/api/placeholder/40/40',
      category: 'attractions',
      tags: ['medina', 'hidden gems', 'authentic', 'culture'],
      publishedAt: '2024-02-20',
      readTime: 8,
      views: 1250,
      likes: 89,
      comments: 23,
      featured: true,
      image: '/api/placeholder/600/300'
    },
    {
      id: 2,
      title: 'A Food Lover\'s Guide to Marrakech Street Food',
      excerpt: 'Navigate the bustling food scene of Jemaa el-Fnaa and discover the best street food vendors, from traditional tagines to modern fusion dishes.',
      content: 'Full article content would go here...',
      author: 'Aicha Mansouri',
      authorAvatar: '/api/placeholder/40/40',
      category: 'food',
      tags: ['street food', 'jemaa el-fnaa', 'local cuisine', 'vendors'],
      publishedAt: '2024-02-18',
      readTime: 6,
      views: 980,
      likes: 67,
      comments: 15,
      featured: false,
      image: '/api/placeholder/600/300'
    },
    {
      id: 3,
      title: 'The Art of Moroccan Hospitality: What to Expect',
      excerpt: 'Understanding Moroccan culture and hospitality customs will enhance your travel experience. Learn about traditions, etiquette, and how to show respect.',
      content: 'Full article content would go here...',
      author: 'Omar Ziani',
      authorAvatar: '/api/placeholder/40/40',
      category: 'culture',
      tags: ['hospitality', 'culture', 'traditions', 'etiquette'],
      publishedAt: '2024-02-15',
      readTime: 5,
      views: 756,
      likes: 45,
      comments: 12,
      featured: false,
      image: '/api/placeholder/600/300'
    },
    {
      id: 4,
      title: 'Best Time to Visit Marrakech: A Seasonal Guide',
      excerpt: 'Plan your perfect trip to Marrakech with our comprehensive seasonal guide. Learn about weather, festivals, and the best activities for each time of year.',
      content: 'Full article content would go here...',
      author: 'Youssef Benali',
      authorAvatar: '/api/placeholder/40/40',
      category: 'travel-tips',
      tags: ['planning', 'weather', 'seasons', 'festivals'],
      publishedAt: '2024-02-12',
      readTime: 7,
      views: 1420,
      likes: 102,
      comments: 28,
      featured: true,
      image: '/api/placeholder/600/300'
    },
    {
      id: 5,
      title: 'Exploring the Atlas Mountains: Day Trips from Marrakech',
      excerpt: 'Escape the city heat and discover the stunning Atlas Mountains. Our guide covers the best day trips, hiking trails, and Berber village experiences.',
      content: 'Full article content would go here...',
      author: 'Omar Ziani',
      authorAvatar: '/api/placeholder/40/40',
      category: 'nature',
      tags: ['atlas mountains', 'hiking', 'berber villages', 'day trips'],
      publishedAt: '2024-02-10',
      readTime: 9,
      views: 892,
      likes: 73,
      comments: 19,
      featured: false,
      image: '/api/placeholder/600/300'
    },
    {
      id: 6,
      title: 'Shopping in Marrakech: Souks, Markets, and Bargaining Tips',
      excerpt: 'Master the art of shopping in Marrakech\'s famous souks. Learn bargaining techniques, find the best markets, and discover authentic Moroccan crafts.',
      content: 'Full article content would go here...',
      author: 'Aicha Mansouri',
      authorAvatar: '/api/placeholder/40/40',
      category: 'shopping',
      tags: ['souks', 'shopping', 'bargaining', 'crafts'],
      publishedAt: '2024-02-08',
      readTime: 6,
      views: 1100,
      likes: 85,
      comments: 31,
      featured: false,
      image: '/api/placeholder/600/300'
    }
  ];

  const categories = [
    { value: 'all', label: 'All Posts' },
    { value: 'attractions', label: 'Attractions' },
    { value: 'food', label: 'Food & Cuisine' },
    { value: 'culture', label: 'Culture' },
    { value: 'travel-tips', label: 'Travel Tips' },
    { value: 'nature', label: 'Nature' },
    { value: 'shopping', label: 'Shopping' }
  ];

  const sortOptions = [
    { value: 'latest', label: 'Latest Posts' },
    { value: 'popular', label: 'Most Popular' },
    { value: 'trending', label: 'Trending' }
  ];

  const filteredPosts = blogPosts.filter(post => {
    const matchesCategory = selectedCategory === 'all' || post.category === selectedCategory;
    const matchesSearch = post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.excerpt.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         post.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const sortedPosts = [...filteredPosts].sort((a, b) => {
    switch (sortBy) {
      case 'popular':
        return b.views - a.views;
      case 'trending':
        return b.likes - a.likes;
      default:
        return new Date(b.publishedAt) - new Date(a.publishedAt);
    }
  });

  const featuredPosts = sortedPosts.filter(post => post.featured);
  const regularPosts = sortedPosts.filter(post => !post.featured);

  const BlogCard = ({ post, featured = false }) => (
    <Card className={`hover:shadow-xl transition-all duration-300 ${featured ? 'lg:col-span-2' : ''}`}>
      <div className={`${featured ? 'lg:flex' : ''}`}>
        <div className={`${featured ? 'lg:w-1/2' : ''} relative`}>
          <img 
            src={post.image} 
            alt={post.title}
            className={`w-full object-cover ${featured ? 'h-64 lg:h-full' : 'h-48'}`}
          />
          {featured && (
            <Badge className="absolute top-4 left-4 bg-orange-500 hover:bg-orange-600">
              Featured
            </Badge>
          )}
        </div>
        <div className={`${featured ? 'lg:w-1/2' : ''}`}>
          <CardHeader>
            <div className="flex items-center justify-between mb-2">
              <Badge variant="secondary">
                {categories.find(cat => cat.value === post.category)?.label}
              </Badge>
              <div className="flex items-center text-sm text-gray-500">
                <Calendar className="h-3 w-3 mr-1" />
                {new Date(post.publishedAt).toLocaleDateString()}
              </div>
            </div>
            <CardTitle className={`${featured ? 'text-2xl' : 'text-xl'} hover:text-orange-600 transition-colors`}>
              <Link to={`/blog/${post.id}`}>
                {post.title}
              </Link>
            </CardTitle>
            <CardDescription className="text-base">
              {post.excerpt}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <img 
                  src={post.authorAvatar} 
                  alt={post.author}
                  className="w-8 h-8 rounded-full"
                />
                <span className="text-sm font-medium">{post.author}</span>
              </div>
              <div className="flex items-center text-sm text-gray-500">
                <Clock className="h-3 w-3 mr-1" />
                {post.readTime} min read
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex space-x-4 text-sm text-gray-500">
                <span className="flex items-center">
                  <Eye className="h-3 w-3 mr-1" />
                  {post.views}
                </span>
                <span className="flex items-center">
                  <Heart className="h-3 w-3 mr-1" />
                  {post.likes}
                </span>
                <span className="flex items-center">
                  <MessageCircle className="h-3 w-3 mr-1" />
                  {post.comments}
                </span>
              </div>
              <Button variant="link" className="p-0 text-orange-600">
                Read More <ArrowRight className="h-3 w-3 ml-1" />
              </Button>
            </div>
            
            <div className="flex flex-wrap gap-2 mt-4">
              {post.tags.slice(0, 3).map(tag => (
                <Badge key={tag} variant="outline" className="text-xs">
                  #{tag}
                </Badge>
              ))}
            </div>
          </CardContent>
        </div>
      </div>
    </Card>
  );

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-orange-500 to-red-600 text-white py-20">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6">Marrakech Blog</h1>
            <p className="text-xl mb-8 opacity-90">
              Insider stories, travel tips, and cultural insights from local experts. 
              Discover the authentic side of Marrakech through our curated articles.
            </p>
            <div className="flex items-center justify-center space-x-6 text-lg">
              <span className="flex items-center">
                <BookOpen className="mr-2 h-5 w-5" />
                {blogPosts.length} Articles
              </span>
              <span className="flex items-center">
                <TrendingUp className="mr-2 h-5 w-5" />
                Weekly Updates
              </span>
              <span className="flex items-center">
                <User className="mr-2 h-5 w-5" />
                Local Authors
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Filters and Search */}
      <section className="py-8 bg-gray-50 border-b">
        <div className="container mx-auto px-4">
          <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
            <div className="flex flex-wrap gap-4 items-center">
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(category => (
                    <SelectItem key={category.value} value={category.value}>
                      {category.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {sortOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search articles..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
            
            <div className="text-sm text-gray-600">
              {sortedPosts.length} articles found
            </div>
          </div>
        </div>
      </section>

      {/* Featured Posts */}
      {featuredPosts.length > 0 && (
        <section className="py-12">
          <div className="container mx-auto px-4">
            <div className="flex items-center mb-8">
              <TrendingUp className="h-6 w-6 text-orange-600 mr-2" />
              <h2 className="text-3xl font-bold">Featured Articles</h2>
            </div>
            <div className="grid lg:grid-cols-2 gap-8">
              {featuredPosts.map(post => (
                <BlogCard key={post.id} post={post} featured={true} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Regular Posts */}
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center mb-8">
            <BookOpen className="h-6 w-6 text-orange-600 mr-2" />
            <h2 className="text-3xl font-bold">Latest Articles</h2>
          </div>
          
          {regularPosts.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No articles found</h3>
              <p className="text-gray-600">Try adjusting your search or filter criteria</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {regularPosts.map(post => (
                <BlogCard key={post.id} post={post} />
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Newsletter Signup */}
      <section className="py-16 bg-gradient-to-r from-orange-600 to-red-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">Stay Updated</h2>
          <p className="text-xl mb-8 opacity-90">
            Get the latest articles and travel tips delivered to your inbox
          </p>
          <div className="max-w-md mx-auto flex gap-4">
            <Input 
              placeholder="Enter your email" 
              className="bg-white text-gray-900"
            />
            <Button variant="secondary" className="text-orange-600 whitespace-nowrap">
              Subscribe
            </Button>
          </div>
          <p className="text-sm opacity-75 mt-4">
            No spam, unsubscribe at any time
          </p>
        </div>
      </section>

      {/* Popular Tags */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">Popular Topics</h2>
            <p className="text-gray-600">Explore articles by popular tags</p>
          </div>
          
          <div className="flex flex-wrap justify-center gap-3">
            {['medina', 'food', 'culture', 'atlas mountains', 'souks', 'riads', 'desert', 'festivals', 'photography', 'travel tips'].map(tag => (
              <Badge 
                key={tag} 
                variant="outline" 
                className="text-sm px-4 py-2 hover:bg-orange-50 hover:border-orange-300 cursor-pointer transition-colors"
              >
                <Tag className="h-3 w-3 mr-1" />
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default BlogPage;

