# 🏛️ Marrakech Reviews - Travel Platform

A modern, full-stack travel review platform for discovering the best experiences in Marrakech, Morocco. Built with React, Flask, and MongoDB.

![Marrakech Reviews](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![React](https://img.shields.io/badge/Frontend-React%2018-blue)
![Flask](https://img.shields.io/badge/Backend-Flask-red)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-green)

## ✨ Features

### 🎯 Core Features
- **Travel Articles**: Comprehensive guides and insider tips
- **Review System**: User reviews with ratings and photos
- **Search & Filter**: Find experiences by category, location, rating
- **User Authentication**: Secure login/registration system
- **Admin Dashboard**: Content management and user administration
- **Responsive Design**: Perfect on desktop and mobile devices

### 🔧 Technical Features
- **Modern React Frontend**: Built with Vite, Tailwind CSS
- **RESTful API**: Flask backend with comprehensive endpoints
- **MongoDB Database**: Scalable NoSQL data storage
- **JWT Authentication**: Secure token-based authentication
- **Image Upload**: Cloudinary integration for media management
- **Email System**: SMTP integration for notifications
- **Social Login**: Google and Facebook OAuth integration

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB (local or cloud)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/marrakech-reviews.git
cd marrakech-reviews
```

2. **Backend Setup**
```bash
cd marrakech-backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python src/main.py
```

3. **Frontend Setup**
```bash
cd marrakech-frontend
npm install
cp .env.example .env
# Edit .env with your backend URL
npm run dev
```

4. **Access the Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

## 📁 Project Structure

```
marrakech-enhanced-project/
├── marrakech-frontend/          # React frontend
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── lib/               # API and utilities
│   │   └── contexts/          # React contexts
│   ├── public/                # Static assets
│   └── package.json
├── marrakech-backend/           # Flask backend
│   ├── src/
│   │   ├── routes/            # API endpoints
│   │   ├── models/            # Database models
│   │   └── utils/             # Helper functions
│   ├── requirements.txt
│   └── main.py
├── vercel.json                  # Deployment config
├── .env.example                 # Environment template
└── DEPLOYMENT_GUIDE.md         # Deployment instructions
```

## 🌐 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Articles
- `GET /api/v1/articles` - Get all articles
- `GET /api/v1/articles/:id` - Get article by ID
- `POST /api/v1/articles` - Create new article (admin)

### Reviews
- `GET /api/v1/reviews` - Get all reviews
- `GET /api/v1/reviews/:id` - Get review by ID
- `POST /api/v1/reviews` - Create new review

### Users
- `GET /api/v1/users` - Get all users (admin)
- `PUT /api/v1/users/:id` - Update user
- `DELETE /api/v1/users/:id` - Delete user (admin)

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
MONGODB_URI=mongodb://localhost:27017/marrakech_reviews
JWT_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api/v1
```

## 🚀 Deployment

### Vercel (Frontend)
1. Connect your GitHub repository to Vercel
2. Set root directory to `marrakech-frontend`
3. Add environment variable: `VITE_API_URL`
4. Deploy automatically on push

### Railway/Heroku (Backend)
1. Connect your repository
2. Set environment variables
3. Deploy the `marrakech-backend` directory

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 📊 Sample Data

The application includes sample data:
- **3 Travel Articles**: Jemaa el-Fna, Majorelle Garden, Best Riads
- **2 User Reviews**: Detailed reviews with ratings
- **Admin User**: admin@marrakechreviews.com / SecureAdmin123!
- **Regular User**: user@example.com / password123

## 🎨 Screenshots

### Homepage
Beautiful landing page with featured content and navigation.

### Articles Page
Comprehensive travel guides with images and detailed information.

### Reviews Page
User reviews with ratings, photos, and helpful voting system.

### Admin Dashboard
Content management interface for administrators.

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI library
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **React Query** - Data fetching and caching

### Backend
- **Flask** - Python web framework
- **MongoDB** - NoSQL database
- **PyMongo** - MongoDB driver
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing
- **Werkzeug** - Password hashing

## 🔒 Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- CORS protection
- Input validation and sanitization
- Rate limiting (configurable)
- Environment-based configuration

## 📱 Mobile Responsive

The application is fully responsive and works perfectly on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Open an issue on GitHub
- Review the API documentation

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced search filters
- [ ] Real-time notifications
- [ ] Mobile app (React Native)
- [ ] Integration with booking platforms
- [ ] AI-powered recommendations

---

**Built with ❤️ for travelers exploring the beautiful city of Marrakech**

#   M a r r a k e c h - R e v i e w s - P l a t f o r m  
 #   M a r r a k e c h - R e v i e w s - P l a t f o r m  
 #   M a r r a k e c h - R e v i e w s - P l a t f o r m  
 #   M a r r a k e c h - R e v i e w s - P l a t f o r m  
 