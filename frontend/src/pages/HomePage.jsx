import React from 'react';
import { Link } from 'react-router-dom';
import { Search, MapPin, Star, MessageSquare, FileText, Gift } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20 px-4 text-center">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">Discover the Magic of Marrakech</h1>
          <p className="text-lg md:text-xl mb-8">Your ultimate guide to reviews, articles, and hidden gems in the Red City.</p>
          <div className="flex justify-center space-x-4">
            <Link to="/reviews" className="bg-white text-blue-600 px-6 py-3 rounded-full font-semibold shadow-lg hover:bg-gray-100 transition duration-300">
              <MessageSquare className="inline-block w-5 h-5 mr-2" />
              Explore Reviews
            </Link>
            <Link to="/articles" className="bg-transparent border border-white text-white px-6 py-3 rounded-full font-semibold hover:bg-white hover:text-blue-600 transition duration-300">
              <FileText className="inline-block w-5 h-5 mr-2" />
              Read Articles
            </Link>
          </div>
        </div>
      </section>

      {/* Search Bar Section */}
      <section className="-mt-10 mb-12 px-4">
        <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-xl p-6 md:p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">Find Your Next Adventure</h2>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-grow">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search for places, reviews, articles..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-300">
              Search
            </button>
          </div>
        </div>
      </section>

      {/* Featured Categories/Spots */}
      <section className="py-12 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">Top Categories & Must-Visit Spots</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Link to="/articles?category=attractions" className="group block bg-gray-100 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition duration-300">
              <img src="https://via.placeholder.com/400x250/FFD700/FFFFFF?text=Jemaa+el-Fna" alt="Jemaa el-Fna" className="w-full h-48 object-cover group-hover:scale-105 transition duration-300" />
              <div className="p-4">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Jemaa el-Fna</h3>
                <p className="text-gray-600 text-sm">The vibrant heart of Marrakech, a UNESCO World Heritage site.</p>
              </div>
            </Link>
            <Link to="/articles?category=gardens" className="group block bg-gray-100 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition duration-300">
              <img src="https://via.placeholder.com/400x250/8A2BE2/FFFFFF?text=Majorelle+Garden" alt="Majorelle Garden" className="w-full h-48 object-cover group-hover:scale-105 transition duration-300" />
              <div className="p-4">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Majorelle Garden</h3>
                <p className="text-gray-600 text-sm">An enchanting botanical garden with vibrant blue buildings.</p>
              </div>
            </Link>
            <Link to="/articles?category=palaces" className="group block bg-gray-100 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition duration-300">
              <img src="https://via.placeholder.com/400x250/A52A2A/FFFFFF?text=Bahia+Palace" alt="Bahia Palace" className="w-full h-48 object-cover group-hover:scale-105 transition duration-300" />
              <div className="p-4">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Bahia Palace</h3>
                <p className="text-gray-600 text-sm">A stunning 19th-century palace showcasing Moroccan architecture.</p>
              </div>
            </Link>
            <Link to="/articles?category=markets" className="group block bg-gray-100 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition duration-300">
              <img src="https://via.placeholder.com/400x250/228B22/FFFFFF?text=Souks" alt="Marrakech Souks" className="w-full h-48 object-cover group-hover:scale-105 transition duration-300" />
              <div className="p-4">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Marrakech Souks</h3>
                <p className="text-gray-600 text-sm">Explore the labyrinthine markets for unique treasures.</p>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Call to Action - Reviews */}
      <section className="bg-blue-50 py-16 px-4 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Share Your Marrakech Experience</h2>
          <p className="text-lg text-gray-600 mb-8">Help fellow travelers by sharing your honest reviews of places you've visited.</p>
          <Link to="/reviews/new" className="bg-blue-600 text-white px-8 py-4 rounded-full font-semibold shadow-lg hover:bg-blue-700 transition duration-300">
            <Star className="inline-block w-5 h-5 mr-2" />
            Write a Review
          </Link>
        </div>
      </section>

      {/* Articles Preview (Placeholder) */}
      <section className="py-12 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">Latest Travel Guides & Tips</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Placeholder Article Card 1 */}
            <div className="bg-gray-100 rounded-lg shadow-md overflow-hidden">
              <img src="https://via.placeholder.com/400x250/FF6347/FFFFFF?text=Article+1" alt="Article 1" className="w-full h-48 object-cover" />
              <div className="p-4">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Exploring the Medina</h3>
                <p className="text-gray-600 text-sm mb-4">A deep dive into the bustling alleys and hidden gems of Marrakech's old city.</p>
                <Link to="/articles/exploring-the-medina" className="text-blue-600 hover:underline font-medium">
                  Read More <span aria-hidden="true">&rarr;</span>
                </Link>
              </div>
            </div>
            {/* Placeholder Article Card 2 */}
            <div className="bg-gray-100 rounded-lg shadow-md overflow-hidden">
              <img src="https://via.placeholder.com/400x250/4682B4/FFFFFF?text=Article+2" alt="Article 2" className="w-full h-48 object-cover" />
              <div className="p-4">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Marrakech Cuisine Guide</h3>
                <p className="text-gray-600 text-sm mb-4">Savor the flavors of Morocco with our guide to the best food spots.</p>
                <Link to="/articles/marrakech-cuisine-guide" className="text-blue-600 hover:underline font-medium">
                  Read More <span aria-hidden="true">&rarr;</span>
                </Link>
              </div>
            </div>
            {/* Placeholder Article Card 3 */}
            <div className="bg-gray-100 rounded-lg shadow-md overflow-hidden">
              <img src="https://via.placeholder.com/400x250/DA70D6/FFFFFF?text=Article+3" alt="Article 3" className="w-full h-48 object-cover" />
              <div className="p-4">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Day Trips from Marrakech</h3>
                <p className="text-gray-600 text-sm mb-4">Discover exciting excursions to the Atlas Mountains and coastal towns.</p>
                <Link to="/articles/day-trips-from-marrakech" className="text-blue-600 hover:underline font-medium">
                  Read More <span aria-hidden="true">&rarr;</span>
                </Link>
              </div>
            </div>
          </div>
          <div className="text-center mt-10">
            <Link to="/articles" className="bg-gray-200 text-gray-800 px-6 py-3 rounded-full font-semibold hover:bg-gray-300 transition duration-300">
              View All Articles
            </Link>
          </div>
        </div>
      </section>

      {/* User Benefits/Call to Action */}
      <section className="bg-purple-700 text-white py-16 px-4 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Join Our Community!</h2>
          <p className="text-lg md:text-xl mb-8">Sign up today to write reviews, save your favorite spots, and get exclusive weekly coupons!</p>
          <div className="flex justify-center space-x-4">
            <Link to="/register" className="bg-white text-purple-700 px-6 py-3 rounded-full font-semibold shadow-lg hover:bg-gray-100 transition duration-300">
              <Gift className="inline-block w-5 h-5 mr-2" />
              Register Now
            </Link>
            <Link to="/login" className="bg-transparent border border-white text-white px-6 py-3 rounded-full font-semibold hover:bg-white hover:text-purple-700 transition duration-300">
              Login
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;

