import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, Star, ThumbsUp, Heart, MapPin, User, Calendar } from 'lucide-react';
import { reviewsAPI } from '../lib/api';

const ReviewsPage = () => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPlaceType, setSelectedPlaceType] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [pagination, setPagination] = useState({});

  const placeTypes = [
    'All Types',
    'Restaurant',
    'Hotel/Riad',
    'Attraction',
    'Shopping',
    'Activities',
    'Hidden Gems'
  ];

  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'rating', label: 'Highest Rated' },
    { value: 'helpful', label: 'Most Helpful' }
  ];

  useEffect(() => {
    fetchReviews();
  }, [selectedPlaceType, searchTerm, sortBy]);

  const fetchReviews = async (page = 1) => {
    try {
      setLoading(true);
      const params = {
        page,
        limit: 12
      };
      
      if (selectedPlaceType && selectedPlaceType !== 'All Types') {
        params.placeType = selectedPlaceType;
      }
      
      if (searchTerm) {
        params.search = searchTerm;
      }

      const response = await reviewsAPI.getReviews(params);
      let reviewsData = response.data.reviews;

      // Client-side sorting since backend doesn't support it yet
      if (sortBy === 'rating') {
        reviewsData.sort((a, b) => b.rating - a.rating);
      } else if (sortBy === 'helpful') {
        reviewsData.sort((a, b) => b.helpful - a.helpful);
      } else if (sortBy === 'oldest') {
        reviewsData.sort((a, b) => new Date(a.date) - new Date(b.date));
      } else {
        reviewsData.sort((a, b) => new Date(b.date) - new Date(a.date));
      }

      setReviews(reviewsData);
      setPagination(response.data.pagination);
      setError(null);
    } catch (err) {
      setError('Failed to load reviews. Please try again.');
      console.error('Error fetching reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchReviews(1);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  if (loading && reviews.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading reviews...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">Reviews & Experiences</h1>
            <p className="text-xl text-red-100 max-w-2xl mx-auto">
              Real experiences from travelers who have explored Marrakech's best places
            </p>
            <div className="mt-6">
              <Link
                to="/reviews/add"
                className="inline-block bg-white text-red-600 font-semibold px-6 py-3 rounded-lg hover:bg-gray-100 transition-colors"
              >
                Write a Review
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filter Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search Bar */}
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="text"
                  placeholder="Search reviews..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
            </form>

            {/* Place Type Filter */}
            <div className="flex items-center gap-2">
              <Filter className="text-gray-400 h-5 w-5" />
              <select
                value={selectedPlaceType}
                onChange={(e) => setSelectedPlaceType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                {placeTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort Options */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            >
              {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-600">{error}</p>
            <button
              onClick={() => fetchReviews()}
              className="mt-2 text-red-600 hover:text-red-800 underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Reviews Grid */}
        {reviews.length > 0 ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {reviews.map((review) => (
                <article key={review.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                  {/* Review Header */}
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="inline-block bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                            {review.placeType}
                          </span>
                          <div className="flex items-center">
                            {renderStars(review.rating)}
                            <span className="ml-1 text-sm text-gray-600">({review.rating})</span>
                          </div>
                        </div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-2">
                          <Link 
                            to={`/reviews/${review.id}`}
                            className="hover:text-red-600 transition-colors"
                          >
                            {review.title}
                          </Link>
                        </h2>
                        <div className="flex items-center text-gray-500 text-sm mb-3">
                          <MapPin className="h-4 w-4 mr-1" />
                          <span>{review.location}</span>
                        </div>
                      </div>
                    </div>

                    {/* Review Content */}
                    <p className="text-gray-600 mb-4 line-clamp-3">
                      {review.excerpt}
                    </p>

                    {/* Review Image */}
                    {review.images && review.images.length > 0 && (
                      <div className="mb-4">
                        <img
                          src={review.images[0]}
                          alt={review.title}
                          className="w-full h-48 object-cover rounded-lg"
                        />
                      </div>
                    )}

                    {/* Tags */}
                    {review.tags && review.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-4">
                        {review.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Review Footer */}
                    <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                      <div className="flex items-center text-sm text-gray-500">
                        <User className="h-4 w-4 mr-1" />
                        <span className="font-medium">{review.author.fullName}</span>
                        <span className="mx-2">•</span>
                        <Calendar className="h-4 w-4 mr-1" />
                        <span>{formatDate(review.date)}</span>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center">
                          <Heart className="h-4 w-4 mr-1" />
                          <span>{review.likes}</span>
                        </div>
                        <div className="flex items-center">
                          <ThumbsUp className="h-4 w-4 mr-1" />
                          <span>{review.helpful}</span>
                        </div>
                      </div>
                    </div>

                    {/* Read More Button */}
                    <div className="mt-4">
                      <Link
                        to={`/reviews/${review.id}`}
                        className="inline-flex items-center text-red-600 hover:text-red-800 font-medium"
                      >
                        Read Full Review
                        <svg className="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </Link>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            {/* Pagination */}
            {pagination.pages > 1 && (
              <div className="flex justify-center">
                <nav className="flex items-center space-x-2">
                  {pagination.page > 1 && (
                    <button
                      onClick={() => fetchReviews(pagination.page - 1)}
                      className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Previous
                    </button>
                  )}
                  
                  {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((page) => (
                    <button
                      key={page}
                      onClick={() => fetchReviews(page)}
                      className={`px-3 py-2 text-sm font-medium rounded-md ${
                        page === pagination.page
                          ? 'bg-red-600 text-white'
                          : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  ))}
                  
                  {pagination.page < pagination.pages && (
                    <button
                      onClick={() => fetchReviews(pagination.page + 1)}
                      className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Next
                    </button>
                  )}
                </nav>
              </div>
            )}
          </>
        ) : (
          !loading && (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No reviews found</h3>
              <p className="text-gray-500 mb-4">
                {searchTerm || selectedPlaceType !== 'All Types'
                  ? 'Try adjusting your search or filter criteria.'
                  : 'Be the first to share your Marrakech experience!'}
              </p>
              <Link
                to="/reviews/add"
                className="inline-block bg-red-600 text-white font-semibold px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
              >
                Write the First Review
              </Link>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default ReviewsPage;

