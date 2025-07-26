import React, { useState, useEffect } from 'react';
import { reviewsAPI } from '../lib/api';

const ReviewsPageSimple = () => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('ReviewsPageSimple mounted');
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      console.log('Fetching reviews...');
      setLoading(true);
      const response = await reviewsAPI.getReviews();
      console.log('Reviews response:', response);
      setReviews(response.data || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching reviews:', err);
      setError('Failed to load reviews. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className={`text-lg ${i < rating ? 'text-yellow-400' : 'text-gray-300'}`}>
        ★
      </span>
    ));
  };

  console.log('ReviewsPageSimple render - loading:', loading, 'reviews:', reviews.length, 'error:', error);

  if (loading) {
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

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={fetchReviews}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-red-600 to-orange-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">Reviews & Experiences</h1>
            <p className="text-xl text-red-100 max-w-2xl mx-auto">
              Real experiences from travelers who have explored Marrakech's best places
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Reviews ({reviews.length})</h2>
        </div>

        {reviews.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No reviews found.</p>
            <button className="mt-4 px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700">
              Write the First Review
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {reviews.map((review) => (
              <div key={review._id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold mb-2">{review.title}</h3>
                    <div className="flex items-center mb-2">
                      {renderStars(review.rating)}
                      <span className="ml-2 text-gray-600">({review.rating}/5)</span>
                    </div>
                    <p className="text-sm text-gray-500">
                      {review.location?.name} • {review.location?.type}
                    </p>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(review.createdAt).toLocaleDateString()}
                  </div>
                </div>
                
                <p className="text-gray-700 mb-4">{review.content}</p>
                
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <div className="flex space-x-4">
                    <span>👍 {review.helpful} helpful</span>
                    <span>❤️ {review.likes} likes</span>
                  </div>
                  {review.tags && review.tags.length > 0 && (
                    <div className="flex space-x-2">
                      {review.tags.map((tag, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 rounded-full text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewsPageSimple;

