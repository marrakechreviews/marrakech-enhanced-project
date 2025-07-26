import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Star, MapPin, Tag, Upload, AlertCircle, CheckCircle } from 'lucide-react';
import { reviewsAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const AddReviewPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    title: '',
    content: '',
    rating: 0,
    placeType: '',
    location: '',
    tags: ''
  });

  const [hoverRating, setHoverRating] = useState(0);

  const placeTypes = [
    'Restaurant',
    'Hotel/Riad',
    'Attraction',
    'Shopping',
    'Activities',
    'Hidden Gems'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRatingClick = (rating) => {
    setFormData(prev => ({
      ...prev,
      rating
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!user) {
      setError('Please log in to write a review.');
      return;
    }

    if (!formData.title || !formData.content || !formData.rating || !formData.placeType || !formData.location) {
      setError('Please fill in all required fields.');
      return;
    }

    if (formData.content.length < 50) {
      setError('Review content must be at least 50 characters long.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const reviewData = {
        ...formData,
        tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag) : []
      };

      await reviewsAPI.createReview(reviewData);
      setSuccess(true);
      
      // Redirect after success
      setTimeout(() => {
        navigate('/reviews');
      }, 2000);
      
    } catch (err) {
      setError(err.message || 'Failed to submit review. Please try again.');
      console.error('Error creating review:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (interactive = false) => {
    return Array.from({ length: 5 }, (_, i) => {
      const starValue = i + 1;
      const isActive = interactive ? 
        (hoverRating >= starValue || (!hoverRating && formData.rating >= starValue)) :
        formData.rating >= starValue;

      return (
        <Star
          key={i}
          className={`h-8 w-8 cursor-pointer transition-colors ${
            isActive ? 'text-yellow-400 fill-current' : 'text-gray-300 hover:text-yellow-200'
          }`}
          onClick={interactive ? () => handleRatingClick(starValue) : undefined}
          onMouseEnter={interactive ? () => setHoverRating(starValue) : undefined}
          onMouseLeave={interactive ? () => setHoverRating(0) : undefined}
        />
      );
    });
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow-sm p-8 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Review Submitted Successfully!</h2>
            <p className="text-gray-600 mb-6">
              Thank you for sharing your experience. Your review will help other travelers discover amazing places in Marrakech.
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                to="/reviews"
                className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
              >
                View All Reviews
              </Link>
              <button
                onClick={() => {
                  setSuccess(false);
                  setFormData({
                    title: '',
                    content: '',
                    rating: 0,
                    placeType: '',
                    location: '',
                    tags: ''
                  });
                }}
                className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Write Another Review
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link
            to="/reviews"
            className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Reviews
          </Link>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Write a Review</h1>
            <p className="text-gray-600">
              Share your experience and help fellow travelers discover the best of Marrakech
            </p>
          </div>

          {!user && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-yellow-600 mr-2" />
                <p className="text-yellow-800">
                  Please <Link to="/login" className="underline font-medium">log in</Link> to write a review.
                </p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Place Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Place Type <span className="text-red-500">*</span>
              </label>
              <select
                name="placeType"
                value={formData.placeType}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="">Select a place type</option>
                {placeTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="e.g., Amazing rooftop dining experience"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="e.g., Medina, Marrakech"
                  required
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Rating */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rating <span className="text-red-500">*</span>
              </label>
              <div className="flex items-center gap-2">
                <div className="flex">
                  {renderStars(true)}
                </div>
                <span className="text-sm text-gray-600">
                  {formData.rating > 0 ? `${formData.rating} star${formData.rating !== 1 ? 's' : ''}` : 'Click to rate'}
                </span>
              </div>
            </div>

            {/* Review Content */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Review <span className="text-red-500">*</span>
              </label>
              <textarea
                name="content"
                value={formData.content}
                onChange={handleInputChange}
                rows={8}
                placeholder="Share your detailed experience... What did you like? What could be improved? Any tips for other travelers?"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
              />
              <div className="flex justify-between mt-1">
                <p className="text-sm text-gray-500">Minimum 50 characters</p>
                <p className="text-sm text-gray-500">{formData.content.length} characters</p>
              </div>
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags (Optional)
              </label>
              <div className="relative">
                <Tag className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="text"
                  name="tags"
                  value={formData.tags}
                  onChange={handleInputChange}
                  placeholder="e.g., romantic, family-friendly, budget (separate with commas)"
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Add relevant tags to help others find your review
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
                  <p className="text-red-600">{error}</p>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading || !user}
                className="flex-1 bg-red-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Submitting...
                  </div>
                ) : (
                  'Submit Review'
                )}
              </button>
              <Link
                to="/reviews"
                className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </Link>
            </div>
          </form>

          {/* Guidelines */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Review Guidelines</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                Be honest and detailed about your experience
              </li>
              <li className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                Include specific details that would help other travelers
              </li>
              <li className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                Be respectful and constructive in your feedback
              </li>
              <li className="flex items-start">
                <span className="text-red-500 mr-2">•</span>
                Avoid personal information or inappropriate content
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddReviewPage;

