import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter, Clock, User, Tag } from 'lucide-react';
import { articlesAPI } from '../lib/api';

const ArticlesPage = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [pagination, setPagination] = useState({});

  const categories = [
    'All Categories',
    'Shopping',
    'Activities', 
    'Food',
    'Culture',
    'Travel Tips',
    'Hidden Gems'
  ];

  useEffect(() => {
    fetchArticles();
  }, [selectedCategory, searchTerm]);

  const fetchArticles = async (page = 1) => {
    try {
      setLoading(true);
      const params = {
        page,
        limit: 12
      };
      
      if (selectedCategory && selectedCategory !== 'All Categories') {
        params.category = selectedCategory;
      }
      
      if (searchTerm) {
        params.search = searchTerm;
      }

      const response = await articlesAPI.getArticles(params);
      setArticles(response.data.articles);
      setPagination(response.data.pagination);
      setError(null);
    } catch (err) {
      setError('Failed to load articles. Please try again.');
      console.error('Error fetching articles:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchArticles(1);
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading && articles.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading articles...</p>
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
            <h1 className="text-4xl font-bold mb-4">Travel Articles & Guides</h1>
            <p className="text-xl text-red-100 max-w-2xl mx-auto">
              Discover insider tips, local insights, and comprehensive guides to make the most of your Marrakech experience
            </p>
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
                  placeholder="Search articles..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
            </form>

            {/* Category Filter */}
            <div className="flex items-center gap-2">
              <Filter className="text-gray-400 h-5 w-5" />
              <select
                value={selectedCategory}
                onChange={(e) => handleCategoryChange(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-600">{error}</p>
            <button
              onClick={() => fetchArticles()}
              className="mt-2 text-red-600 hover:text-red-800 underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Articles Grid */}
        {articles.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
              {articles.map((article) => (
                <article key={article.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                  {/* Article Image */}
                  <div className="aspect-w-16 aspect-h-9">
                    <img
                      src={article.image || '/api/placeholder/400/250'}
                      alt={article.title}
                      className="w-full h-48 object-cover"
                    />
                  </div>

                  {/* Article Content */}
                  <div className="p-6">
                    {/* Category Badge */}
                    <div className="flex items-center justify-between mb-3">
                      <span className="inline-block bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                        {article.category}
                      </span>
                      <div className="flex items-center text-gray-500 text-sm">
                        <Clock className="h-4 w-4 mr-1" />
                        {article.readTime}
                      </div>
                    </div>

                    {/* Title */}
                    <h2 className="text-xl font-semibold text-gray-900 mb-3 line-clamp-2">
                      <Link 
                        to={`/articles/${article.id}`}
                        className="hover:text-red-600 transition-colors"
                      >
                        {article.title}
                      </Link>
                    </h2>

                    {/* Excerpt */}
                    <p className="text-gray-600 mb-4 line-clamp-3">
                      {article.excerpt}
                    </p>

                    {/* Author and Date */}
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <div className="flex items-center">
                        <User className="h-4 w-4 mr-1" />
                        <span>{article.author.fullName}</span>
                      </div>
                      <span>{formatDate(article.date)}</span>
                    </div>

                    {/* Tags */}
                    {article.tags && article.tags.length > 0 && (
                      <div className="flex items-center mt-3 pt-3 border-t border-gray-100">
                        <Tag className="h-4 w-4 text-gray-400 mr-2" />
                        <div className="flex flex-wrap gap-1">
                          {article.tags.slice(0, 3).map((tag) => (
                            <span
                              key={tag}
                              className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Read More Button */}
                    <div className="mt-4">
                      <Link
                        to={`/articles/${article.id}`}
                        className="inline-flex items-center text-red-600 hover:text-red-800 font-medium"
                      >
                        Read Article
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
                      onClick={() => fetchArticles(pagination.page - 1)}
                      className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Previous
                    </button>
                  )}
                  
                  {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((page) => (
                    <button
                      key={page}
                      onClick={() => fetchArticles(page)}
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
                      onClick={() => fetchArticles(pagination.page + 1)}
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
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No articles found</h3>
              <p className="text-gray-500">
                {searchTerm || selectedCategory !== 'All Categories'
                  ? 'Try adjusting your search or filter criteria.'
                  : 'Check back later for new articles and guides.'}
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default ArticlesPage;

