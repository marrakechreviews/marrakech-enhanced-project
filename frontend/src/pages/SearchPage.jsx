import React, { useState } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Search, MapPin, Star, Filter } from 'lucide-react';

const SearchPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    // Simulate search delay
    setTimeout(() => {
      setIsSearching(false);
    }, 1000);
  };

  const searchResults = [
    {
      id: 1,
      title: "Jemaa el-Fnaa Square",
      type: "review",
      rating: 4.8,
      category: "Attractions",
      location: "Medina, Marrakech",
      excerpt: "The heart of Marrakech comes alive at night with storytellers, musicians, and food vendors.",
      reviewCount: 245
    },
    {
      id: 2,
      title: "Ultimate Guide to Marrakech's Medina",
      type: "article",
      category: "Travel Guide",
      author: "Sarah Johnson",
      excerpt: "Navigate the ancient streets and discover hidden gems in the heart of Marrakech's old city.",
      readTime: "8 min read"
    },
    {
      id: 3,
      title: "Majorelle Garden",
      type: "review",
      rating: 4.6,
      category: "Gardens",
      location: "Gueliz, Marrakech",
      excerpt: "A stunning botanical garden with vibrant blue buildings and exotic plants.",
      reviewCount: 189
    }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Search Marrakech
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Find reviews, articles, and recommendations for the best places in Marrakech
        </p>
      </div>

      {/* Search Form */}
      <div className="max-w-2xl mx-auto mb-12">
        <form onSubmit={handleSearch} className="relative">
          <div className="relative">
            <Search className="absolute left-4 top-4 h-5 w-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Search for places, restaurants, hotels, attractions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 pr-24 py-4 text-lg"
            />
            <Button 
              type="submit" 
              className="absolute right-2 top-2"
              disabled={isSearching}
            >
              {isSearching ? 'Searching...' : 'Search'}
            </Button>
          </div>
        </form>

        {/* Quick Filters */}
        <div className="flex flex-wrap gap-2 mt-4 justify-center">
          <Button variant="outline" size="sm">
            <Filter className="mr-2 h-4 w-4" />
            All
          </Button>
          <Button variant="outline" size="sm">Reviews</Button>
          <Button variant="outline" size="sm">Articles</Button>
          <Button variant="outline" size="sm">Restaurants</Button>
          <Button variant="outline" size="sm">Hotels</Button>
          <Button variant="outline" size="sm">Attractions</Button>
        </div>
      </div>

      {/* Search Results */}
      {searchQuery && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-gray-900">
              Search Results for "{searchQuery}"
            </h2>
            <span className="text-gray-500">
              {searchResults.length} results found
            </span>
          </div>

          <div className="space-y-6">
            {searchResults.map((result) => (
              <Card key={result.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant={result.type === 'review' ? 'default' : 'secondary'}>
                          {result.type === 'review' ? 'Review' : 'Article'}
                        </Badge>
                        <Badge variant="outline">{result.category}</Badge>
                      </div>
                      <CardTitle className="text-xl hover:text-orange-600 cursor-pointer">
                        {result.title}
                      </CardTitle>
                      {result.location && (
                        <div className="flex items-center text-sm text-gray-500 mt-1">
                          <MapPin className="h-4 w-4 mr-1" />
                          {result.location}
                        </div>
                      )}
                    </div>
                    {result.rating && (
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span className="font-semibold">{result.rating}</span>
                        <span className="text-gray-500">({result.reviewCount})</span>
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="mb-4">
                    {result.excerpt}
                  </CardDescription>
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-500">
                      {result.author && `By ${result.author}`}
                      {result.readTime && ` • ${result.readTime}`}
                    </div>
                    <Button variant="outline" size="sm">
                      {result.type === 'review' ? 'Read Review' : 'Read Article'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Load More */}
          <div className="text-center mt-8">
            <Button variant="outline" size="lg">
              Load More Results
            </Button>
          </div>
        </div>
      )}

      {/* Popular Searches */}
      {!searchQuery && (
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
            Popular Searches
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              'Jemaa el-Fnaa',
              'Majorelle Garden',
              'Bahia Palace',
              'Marrakech Restaurants',
              'Riads',
              'Atlas Mountains',
              'Souks Shopping',
              'Hammam Spas'
            ].map((term) => (
              <Button
                key={term}
                variant="outline"
                className="h-auto p-4 text-left justify-start"
                onClick={() => setSearchQuery(term)}
              >
                <Search className="mr-2 h-4 w-4" />
                {term}
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;

