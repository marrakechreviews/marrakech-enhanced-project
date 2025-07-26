# Marrakech Reviews - Deployment Guide

## Overview
This is a full-stack travel review platform with a React frontend and Flask backend. The project has been tested and optimized for deployment.

## Project Structure
```
marrakech-enhanced-project/
├── marrakech-frontend/          # React frontend application
├── marrakech-backend/           # Flask backend API
├── vercel.json                  # Vercel deployment config
├── .env.example                 # Environment variables template
└── DEPLOYMENT_GUIDE.md          # This file
```

## Prerequisites
- Node.js 18+ and npm
- Python 3.11+ and pip
- MongoDB database (local or cloud)
- GitHub account
- Vercel account

## Quick Start (Local Development)

### 1. Backend Setup
```bash
cd marrakech-backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URI and JWT secret
python src/main.py
```

### 2. Frontend Setup
```bash
cd marrakech-frontend
npm install --legacy-peer-deps
cp .env.example .env
# Edit .env with your backend API URL
npm run dev
```

## Deployment to Vercel via GitHub

### Step 1: Prepare Your Repository
1. Create a new GitHub repository
2. Push this entire project to your repository:
```bash
git init
git add .
git commit -m "Initial commit - Marrakech Reviews Platform"
git branch -M main
git remote add origin https://github.com/marrakechreviews/Marrakech.reviews.git

git push -u origin main
```

### Step 2: Deploy Frontend to Vercel
1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "New Project" and import your repository
3. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `marrakech-frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
npm install --legacy-peer-deps
4. Add Environment Variables in Vercel dashboard:
   - `VITE_API_URL`: Your backend API URL (see Step 3)

### Step 3: Deploy Backend
You have several options for backend deployment:

#### Option A: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Select the `marrakech-backend` folder
4. Add environment variables:
   - `MONGODB_URI`: Your MongoDB connection string
   - `JWT_SECRET_KEY`: A secure random string
   - `PORT`: 5000

#### Option B: Heroku
1. Install Heroku CLI
2. Create a new Heroku app
3. Add MongoDB addon or use external MongoDB
4. Set environment variables
5. Deploy using Git

#### Option C: DigitalOcean App Platform
1. Connect your GitHub repository
2. Configure Python app settings
3. Add environment variables
4. Deploy

### Step 4: Configure Environment Variables

#### Frontend (.env)
```env
VITE_API_URL=https://your-backend-url.com/api/v1
```

#### Backend (.env)
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/marrakech_reviews
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters
FLASK_ENV=production
```

### Step 5: Database Setup
1. Create a MongoDB database (MongoDB Atlas recommended)
2. The application will automatically create collections
3. Sample data is included and will be seeded on first run

## API Keys and Configuration

### Required Environment Variables
- `MONGODB_URI`: MongoDB connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens (minimum 32 characters)
- `VITE_API_URL`: Backend API URL for frontend

### Optional Environment Variables
- `GOOGLE_CLIENT_ID`: For Google OAuth login
- `FACEBOOK_APP_ID`: For Facebook login
- `CLOUDINARY_*`: For image uploads
- `SMTP_*`: For email notifications

## Features Included
✅ User authentication and authorization
✅ Article management system
✅ Review and rating system
✅ Admin dashboard
✅ Responsive design
✅ Search and filtering
✅ Image upload support
✅ Email notifications
✅ Social login integration
✅ SEO optimization

## Testing
The application has been thoroughly tested:
- ✅ Homepage loads correctly
- ✅ Articles page displays 3 sample articles
- ✅ Reviews page displays 2 sample reviews
- ✅ Navigation works between all pages
- ✅ Backend APIs return correct data
- ✅ Database is properly seeded
- ✅ Responsive design works on mobile

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure backend allows frontend domain
2. **Environment Variables**: Check all required variables are set
3. **Database Connection**: Verify MongoDB URI is correct
4. **Build Errors**: Check Node.js and Python versions

### Support
- Check the console for error messages
- Verify environment variables are set correctly
- Ensure database is accessible
- Check API endpoints are responding

## Security Notes
- Change all default passwords and secrets
- Use HTTPS in production
- Keep dependencies updated
- Use environment variables for sensitive data
- Enable CORS only for your domains

## Performance Optimization
- Images are optimized for web
- Code splitting is implemented
- Database queries are optimized
- Caching headers are configured

---

**Congratulations!** Your Marrakech Reviews platform is ready for deployment. The application includes sample data and is fully functional out of the box.

