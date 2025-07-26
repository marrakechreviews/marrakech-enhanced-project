import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Clock, User, Tag, Calendar, Share2 } from 'lucide-react';
import { articlesAPI } from '../lib/api';

const ArticleDetailPage = () => {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [relatedArticles, setRelatedArticles] = useState([]);

  useEffect(() => {
    fetchArticle();
    fetchRelatedArticles();
  }, [id]);

  const fetchArticle = async () => {
    try {
      setLoading(true);
      const response = await articlesAPI.getArticle(id);
      setArticle(response.data.article);
      setError(null);
    } catch (err) {
      setError('Article not found or failed to load.');
      console.error('Error fetching article:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRelatedArticles = async () => {
    try {
      const response = await articlesAPI.getArticles({ limit: 3, featured: true });
      setRelatedArticles(response.data.articles.filter(a => a.id !== id));
    } catch (err) {
      console.error('Error fetching related articles:', err);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: article.title,
        text: article.excerpt,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Article link copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading article...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Article not found</h3>
            <p className="text-gray-500 mb-4">{error}</p>
            <Link
              to="/articles"
              className="inline-flex items-center text-red-600 hover:text-red-800 font-medium"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to Articles
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link
            to="/articles"
            className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Articles
          </Link>
        </div>
      </div>

      {/* Article Header */}
      <div className="bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Category Badge */}
          <div className="mb-4">
            <span className="inline-block bg-red-100 text-red-800 text-sm font-medium px-3 py-1 rounded-full">
              {article.category}
            </span>
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-gray-900 mb-6 leading-tight">
            {article.title}
          </h1>

          {/* Article Meta */}
          <div className="flex flex-wrap items-center gap-6 text-gray-600 mb-8">
            <div className="flex items-center">
              <User className="h-5 w-5 mr-2" />
              <span className="font-medium">{article.author.fullName}</span>
            </div>
            <div className="flex items-center">
              <Calendar className="h-5 w-5 mr-2" />
              <span>{formatDate(article.date)}</span>
            </div>
            <div className="flex items-center">
              <Clock className="h-5 w-5 mr-2" />
              <span>{article.readTime}</span>
            </div>
            <button
              onClick={handleShare}
              className="flex items-center text-red-600 hover:text-red-800 transition-colors"
            >
              <Share2 className="h-5 w-5 mr-2" />
              Share
            </button>
          </div>

          {/* Featured Image */}
          {article.image && (
            <div className="mb-8">
              <img
                src={article.image}
                alt={article.title}
                className="w-full h-64 md:h-96 object-cover rounded-lg shadow-sm"
              />
            </div>
          )}
        </div>
      </div>

      {/* Article Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          {/* Article Body */}
          <div className="prose prose-lg max-w-none">
            {article.content.split('\n\n').map((paragraph, index) => (
              <p key={index} className="mb-6 text-gray-700 leading-relaxed">
                {paragraph}
              </p>
            ))}
          </div>

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="mt-8 pt-8 border-t border-gray-200">
              <div className="flex items-center flex-wrap gap-2">
                <Tag className="h-5 w-5 text-gray-400 mr-2" />
                {article.tags.map((tag) => (
                  <span
                    key={tag}
                    className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm hover:bg-gray-200 transition-colors cursor-pointer"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Related Articles */}
        {relatedArticles.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Articles</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {relatedArticles.map((relatedArticle) => (
                <article key={relatedArticle.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                  <div className="aspect-w-16 aspect-h-9">
                    <img
                      src={relatedArticle.image || '/api/placeholder/300/200'}
                      alt={relatedArticle.title}
                      className="w-full h-32 object-cover"
                    />
                  </div>
                  <div className="p-4">
                    <span className="inline-block bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded-full mb-2">
                      {relatedArticle.category}
                    </span>
                    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                      <Link 
                        to={`/articles/${relatedArticle.id}`}
                        className="hover:text-red-600 transition-colors"
                      >
                        {relatedArticle.title}
                      </Link>
                    </h3>
                    <div className="flex items-center text-sm text-gray-500">
                      <Clock className="h-4 w-4 mr-1" />
                      {relatedArticle.readTime}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        )}

        {/* Call to Action */}
        <div className="mt-12 bg-gradient-to-r from-red-600 to-orange-600 rounded-lg p-8 text-center text-white">
          <h3 className="text-2xl font-bold mb-4">Share Your Marrakech Experience</h3>
          <p className="text-red-100 mb-6">
            Have you visited this place or tried these tips? Share your experience with fellow travelers!
          </p>
          <Link
            to="/reviews/add"
            className="inline-block bg-white text-red-600 font-semibold px-6 py-3 rounded-lg hover:bg-gray-100 transition-colors"
          >
            Write a Review
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ArticleDetailPage;

