# Complete API Documentation and Social Login Setup Guide

## Table of Contents
1. [Free APIs for Your Marrakech Travel Website](#free-apis)
2. [Google Login Integration](#google-login)
3. [Facebook Login Integration](#facebook-login)
4. [API Implementation Examples](#implementation-examples)
5. [Security Best Practices](#security)
6. [Rate Limiting and Usage Guidelines](#rate-limiting)

---

## Free APIs for Your Marrakech Travel Website {#free-apis}

This comprehensive guide covers all the free APIs you'll need for your Marrakech travel website, including detailed setup instructions and usage examples.

### 1. Weather API - OpenWeatherMap (Free Tier)

**Purpose:** Display current weather and forecasts for Marrakech
**Free Tier:** 60 calls/minute, 1,000 calls/day
**Website:** https://openweathermap.org/api

#### Setup Instructions:
1. Visit https://openweathermap.org/api
2. Click "Sign Up" and create a free account
3. Verify your email address
4. Go to "API Keys" section in your dashboard
5. Copy your free API key

#### API Endpoints:
- **Current Weather:** `https://api.openweathermap.org/data/2.5/weather?q=Marrakech&appid=YOUR_API_KEY&units=metric`
- **5-Day Forecast:** `https://api.openweathermap.org/data/2.5/forecast?q=Marrakech&appid=YOUR_API_KEY&units=metric`

#### Example Implementation:
```javascript
// Frontend JavaScript
async function getMarrakechWeather() {
    const API_KEY = 'your_openweather_api_key';
    const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=Marrakech&appid=${API_KEY}&units=metric`);
    const data = await response.json();
    
    return {
        temperature: data.main.temp,
        description: data.weather[0].description,
        humidity: data.main.humidity,
        windSpeed: data.wind.speed
    };
}
```

### 2. Maps API - OpenStreetMap with Leaflet (Completely Free)

**Purpose:** Interactive maps for attractions and locations
**Cost:** Completely free, no API key required
**Website:** https://leafletjs.com/

#### Setup Instructions:
1. Include Leaflet CSS and JS in your HTML:
```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

#### Example Implementation:
```javascript
// Initialize map centered on Marrakech
const map = L.map('map').setView([31.6295, -7.9811], 13);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Add marker for Jemaa el-Fnaa
L.marker([31.6260, -7.9890]).addTo(map)
    .bindPopup('Jemaa el-Fnaa Square')
    .openPopup();
```

### 3. Translation API - LibreTranslate (Free & Open Source)

**Purpose:** Translate content for international visitors
**Cost:** Free self-hosted or free tier on hosted service
**Website:** https://libretranslate.com/

#### Setup Instructions:
1. **Option A - Use Public Instance:**
   - Use the free public API at `https://libretranslate.de/translate`
   - No API key required for basic usage

2. **Option B - Self-Host (Recommended):**
   ```bash
   pip install libretranslate
   libretranslate --host 0.0.0.0 --port 5000
   ```

#### Example Implementation:
```javascript
async function translateText(text, targetLang = 'fr') {
    const response = await fetch('https://libretranslate.de/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            q: text,
            source: 'en',
            target: targetLang
        })
    });
    
    const data = await response.json();
    return data.translatedText;
}
```

### 4. Currency Exchange API - ExchangeRate-API (Free Tier)

**Purpose:** Convert prices to different currencies
**Free Tier:** 1,500 requests/month
**Website:** https://exchangerate-api.com/

#### Setup Instructions:
1. Visit https://exchangerate-api.com/
2. Sign up for a free account
3. Get your API key from the dashboard

#### Example Implementation:
```javascript
async function convertCurrency(amount, fromCurrency = 'MAD', toCurrency = 'EUR') {
    const API_KEY = 'your_exchangerate_api_key';
    const response = await fetch(`https://v6.exchangerate-api.com/v6/${API_KEY}/pair/${fromCurrency}/${toCurrency}`);
    const data = await response.json();
    
    return {
        convertedAmount: (amount * data.conversion_rate).toFixed(2),
        rate: data.conversion_rate
    };
}
```

### 5. Image API - Unsplash (Free Tier)

**Purpose:** High-quality images for articles and backgrounds
**Free Tier:** 50 requests/hour
**Website:** https://unsplash.com/developers

#### Setup Instructions:
1. Create an Unsplash account
2. Go to https://unsplash.com/developers
3. Create a new application
4. Get your Access Key

#### Example Implementation:
```javascript
async function getMarrakechImages(query = 'marrakech', count = 10) {
    const ACCESS_KEY = 'your_unsplash_access_key';
    const response = await fetch(`https://api.unsplash.com/search/photos?query=${query}&per_page=${count}&client_id=${ACCESS_KEY}`);
    const data = await response.json();
    
    return data.results.map(photo => ({
        id: photo.id,
        url: photo.urls.regular,
        thumbnail: photo.urls.thumb,
        description: photo.alt_description,
        photographer: photo.user.name
    }));
}
```

### 6. Geocoding API - Nominatim (Free)

**Purpose:** Convert addresses to coordinates and vice versa
**Cost:** Completely free
**Website:** https://nominatim.org/

#### Example Implementation:
```javascript
async function geocodeAddress(address) {
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`);
    const data = await response.json();
    
    if (data.length > 0) {
        return {
            latitude: parseFloat(data[0].lat),
            longitude: parseFloat(data[0].lon),
            displayName: data[0].display_name
        };
    }
    return null;
}
```

### 7. News API - NewsAPI (Free Tier)

**Purpose:** Display travel news and updates about Morocco
**Free Tier:** 1,000 requests/month
**Website:** https://newsapi.org/

#### Setup Instructions:
1. Visit https://newsapi.org/
2. Register for a free account
3. Get your API key

#### Example Implementation:
```javascript
async function getMoroccoNews() {
    const API_KEY = 'your_newsapi_key';
    const response = await fetch(`https://newsapi.org/v2/everything?q=Morocco+travel&sortBy=publishedAt&apiKey=${API_KEY}`);
    const data = await response.json();
    
    return data.articles.slice(0, 5).map(article => ({
        title: article.title,
        description: article.description,
        url: article.url,
        publishedAt: article.publishedAt,
        source: article.source.name
    }));
}
```

---

## Google Login Integration {#google-login}

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console:**
   - Visit https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project:**
   - Click "Select a project" dropdown
   - Click "New Project"
   - Enter project name: "Marrakech Travel Website"
   - Click "Create"

3. **Enable Google+ API:**
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click on it and press "Enable"

### Step 2: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen:**
   - Navigate to "APIs & Services" > "OAuth consent screen"
   - Choose "External" user type
   - Click "Create"

2. **Fill Required Information:**
   ```
   App name: Marrakech Travel Guide
   User support email: your-email@domain.com
   Developer contact information: your-email@domain.com
   ```

3. **Add Scopes:**
   - Click "Add or Remove Scopes"
   - Add: `email`, `profile`, `openid`
   - Save and continue

### Step 3: Create OAuth Credentials

1. **Create Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"

2. **Configure OAuth Client:**
   ```
   Name: Marrakech Travel Web Client
   Authorized JavaScript origins:
   - http://localhost:3000 (for development)
   - https://yourdomain.com (for production)
   
   Authorized redirect URIs:
   - http://localhost:3000/auth/google/callback
   - https://yourdomain.com/auth/google/callback
   ```

3. **Save Credentials:**
   - Copy the Client ID and Client Secret
   - Store them securely in your environment variables

### Step 4: Frontend Implementation

#### Install Google OAuth Library:
```bash
npm install @google-cloud/oauth2
```

#### HTML Setup:
```html
<!-- Add Google Sign-In script -->
<script src="https://accounts.google.com/gsi/client" async defer></script>

<!-- Google Sign-In Button -->
<div id="g_id_onload"
     data-client_id="YOUR_GOOGLE_CLIENT_ID"
     data-callback="handleCredentialResponse">
</div>
<div class="g_id_signin" data-type="standard"></div>
```

#### JavaScript Implementation:
```javascript
// Handle Google Sign-In Response
function handleCredentialResponse(response) {
    // Send the credential to your backend
    fetch('/auth/google', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            credential: response.credential
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirect based on user role
            if (data.user.role === 'admin') {
                window.location.href = '/admin/dashboard';
            } else {
                window.location.href = '/user/dashboard';
            }
        }
    })
    .catch(error => {
        console.error('Login error:', error);
    });
}
```

### Step 5: Backend Implementation (Flask)

#### Install Required Packages:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

#### Flask Route Implementation:
```python
from google.oauth2 import id_token
from google.auth.transport import requests
import os

@app.route('/auth/google', methods=['POST'])
def google_auth():
    try:
        # Get the credential from the request
        credential = request.json.get('credential')
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            credential, 
            requests.Request(), 
            os.getenv('GOOGLE_CLIENT_ID')
        )
        
        # Extract user information
        user_email = idinfo['email']
        user_name = idinfo['name']
        user_picture = idinfo.get('picture', '')
        
        # Check if user exists in database
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            # Create new user
            user = User(
                email=user_email,
                firstName=user_name.split(' ')[0],
                lastName=' '.join(user_name.split(' ')[1:]) if len(user_name.split(' ')) > 1 else '',
                profilePicture=user_picture,
                authProvider='google',
                role='user'  # Default role
            )
            db.session.add(user)
            db.session.commit()
        
        # Create session or JWT token
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.firstName} {user.lastName}",
                'role': user.role
            }
        })
        
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid token'}), 400
```

---

## Facebook Login Integration {#facebook-login}

### Step 1: Create Facebook App

1. **Go to Facebook Developers:**
   - Visit https://developers.facebook.com/
   - Click "My Apps" > "Create App"

2. **Choose App Type:**
   - Select "Consumer"
   - Click "Next"

3. **App Details:**
   ```
   App Name: Marrakech Travel Guide
   App Contact Email: your-email@domain.com
   ```

### Step 2: Configure Facebook Login

1. **Add Facebook Login Product:**
   - In your app dashboard, click "Add Product"
   - Find "Facebook Login" and click "Set Up"

2. **Configure Settings:**
   - Go to "Facebook Login" > "Settings"
   - Add Valid OAuth Redirect URIs:
     ```
     http://localhost:3000/auth/facebook/callback
     https://yourdomain.com/auth/facebook/callback
     ```

3. **Get App Credentials:**
   - Go to "Settings" > "Basic"
   - Copy App ID and App Secret

### Step 3: Frontend Implementation

#### HTML Setup:
```html
<!-- Facebook SDK -->
<script async defer crossorigin="anonymous" 
        src="https://connect.facebook.net/en_US/sdk.js"></script>

<!-- Facebook Login Button -->
<div class="fb-login-button" 
     data-width="" 
     data-size="large" 
     data-button-type="continue_with" 
     data-layout="default" 
     data-auto-logout-link="false" 
     data-use-continue-as="false"
     data-scope="email,public_profile"
     onlogin="checkLoginState();">
</div>
```

#### JavaScript Implementation:
```javascript
// Initialize Facebook SDK
window.fbAsyncInit = function() {
    FB.init({
        appId: 'YOUR_FACEBOOK_APP_ID',
        cookie: true,
        xfbml: true,
        version: 'v18.0'
    });
};

// Check login state
function checkLoginState() {
    FB.getLoginStatus(function(response) {
        if (response.status === 'connected') {
            // User is logged in and authenticated
            getUserInfo();
        }
    });
}

// Get user information
function getUserInfo() {
    FB.api('/me', {fields: 'name,email,picture'}, function(response) {
        // Send user data to backend
        fetch('/auth/facebook', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                accessToken: FB.getAccessToken(),
                userInfo: response
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect based on user role
                if (data.user.role === 'admin') {
                    window.location.href = '/admin/dashboard';
                } else {
                    window.location.href = '/user/dashboard';
                }
            }
        });
    });
}
```

### Step 4: Backend Implementation (Flask)

#### Install Required Packages:
```bash
pip install facebook-sdk
```

#### Flask Route Implementation:
```python
import facebook
import requests

@app.route('/auth/facebook', methods=['POST'])
def facebook_auth():
    try:
        access_token = request.json.get('accessToken')
        user_info = request.json.get('userInfo')
        
        # Verify the access token with Facebook
        graph = facebook.GraphAPI(access_token)
        profile = graph.get_object('me', fields='name,email,picture')
        
        # Extract user information
        user_email = profile.get('email')
        user_name = profile.get('name')
        user_picture = profile.get('picture', {}).get('data', {}).get('url', '')
        
        if not user_email:
            return jsonify({'success': False, 'error': 'Email permission required'}), 400
        
        # Check if user exists in database
        user = User.query.filter_by(email=user_email).first()
        
        if not user:
            # Create new user
            user = User(
                email=user_email,
                firstName=user_name.split(' ')[0],
                lastName=' '.join(user_name.split(' ')[1:]) if len(user_name.split(' ')) > 1 else '',
                profilePicture=user_picture,
                authProvider='facebook',
                role='user'  # Default role
            )
            db.session.add(user)
            db.session.commit()
        
        # Create session
        session['user_id'] = user.id
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.firstName} {user.lastName}",
                'role': user.role
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
```

---

## API Implementation Examples {#implementation-examples}

### Complete Weather Widget Implementation

#### Frontend Component (React):
```jsx
import React, { useState, useEffect } from 'react';

const WeatherWidget = () => {
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchWeather();
    }, []);

    const fetchWeather = async () => {
        try {
            const response = await fetch('/api/weather/marrakech');
            const data = await response.json();
            setWeather(data);
        } catch (error) {
            console.error('Weather fetch error:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Loading weather...</div>;
    if (!weather) return <div>Weather unavailable</div>;

    return (
        <div className="weather-widget">
            <h3>Marrakech Weather</h3>
            <div className="weather-info">
                <div className="temperature">{weather.temperature}°C</div>
                <div className="description">{weather.description}</div>
                <div className="details">
                    <span>Humidity: {weather.humidity}%</span>
                    <span>Wind: {weather.windSpeed} m/s</span>
                </div>
            </div>
        </div>
    );
};

export default WeatherWidget;
```

#### Backend Route (Flask):
```python
@app.route('/api/weather/marrakech')
def get_marrakech_weather():
    try:
        api_key = os.getenv('OPENWEATHER_API_KEY')
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Marrakech&appid={api_key}&units=metric"
        
        response = requests.get(url)
        data = response.json()
        
        weather_data = {
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'].title(),
            'humidity': data['main']['humidity'],
            'windSpeed': data['wind']['speed'],
            'icon': data['weather'][0]['icon']
        }
        
        return jsonify(weather_data)
        
    except Exception as e:
        return jsonify({'error': 'Weather data unavailable'}), 500
```

### Interactive Map with Attractions

#### Frontend Implementation:
```javascript
class MarrakechMap {
    constructor(containerId) {
        this.map = L.map(containerId).setView([31.6295, -7.9811], 13);
        this.initializeMap();
        this.addAttractions();
    }

    initializeMap() {
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
    }

    async addAttractions() {
        try {
            const response = await fetch('/api/attractions');
            const attractions = await response.json();
            
            attractions.forEach(attraction => {
                const marker = L.marker([attraction.latitude, attraction.longitude])
                    .addTo(this.map);
                
                const popupContent = `
                    <div class="attraction-popup">
                        <h4>${attraction.name}</h4>
                        <p>${attraction.description}</p>
                        <a href="/attractions/${attraction.id}">Learn More</a>
                    </div>
                `;
                
                marker.bindPopup(popupContent);
            });
        } catch (error) {
            console.error('Error loading attractions:', error);
        }
    }
}

// Initialize map
document.addEventListener('DOMContentLoaded', () => {
    new MarrakechMap('map');
});
```

---

## Security Best Practices {#security}

### Environment Variables Setup

Create a `.env` file in your project root:
```env
# Weather API
OPENWEATHER_API_KEY=your_openweather_api_key

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Facebook OAuth
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# Other APIs
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
NEWSAPI_KEY=your_newsapi_key
EXCHANGERATE_API_KEY=your_exchangerate_api_key

# Database
DATABASE_URL=your_database_url

# Session Secret
SECRET_KEY=your_secret_key_for_sessions
```

### API Key Security

#### Frontend Security:
```javascript
// Never expose API keys in frontend code
// Instead, create backend proxy endpoints

// ❌ Wrong - API key exposed
const weather = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=Marrakech&appid=${API_KEY}`);

// ✅ Correct - Use backend proxy
const weather = await fetch('/api/weather/marrakech');
```

#### Backend Proxy Implementation:
```python
import os
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('INTERNAL_API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/weather/<city>')
@require_api_key
def get_weather(city):
    # Proxy request to external API with server-side key
    api_key = os.getenv('OPENWEATHER_API_KEY')
    # ... implementation
```

### Rate Limiting Implementation

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/weather/<city>')
@limiter.limit("10 per minute")
def get_weather(city):
    # Implementation with rate limiting
    pass
```

---

## Rate Limiting and Usage Guidelines {#rate-limiting}

### API Usage Limits Summary

| API Service | Free Tier Limit | Recommended Usage |
|-------------|-----------------|-------------------|
| OpenWeatherMap | 60 calls/minute, 1,000/day | Cache responses for 10 minutes |
| Unsplash | 50 requests/hour | Cache images locally |
| NewsAPI | 1,000 requests/month | Update news once daily |
| ExchangeRate-API | 1,500 requests/month | Cache rates for 1 hour |
| LibreTranslate | Unlimited (self-hosted) | No limits if self-hosted |
| OpenStreetMap | Fair use policy | Cache map tiles |

### Caching Implementation

#### Redis Caching (Recommended):
```python
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_api_response(key, data, expiration=600):
    """Cache API response for specified seconds (default 10 minutes)"""
    redis_client.setex(key, expiration, json.dumps(data))

def get_cached_response(key):
    """Get cached API response"""
    cached = redis_client.get(key)
    return json.loads(cached) if cached else None

@app.route('/api/weather/<city>')
def get_weather_cached(city):
    cache_key = f"weather:{city}"
    
    # Try to get from cache first
    cached_weather = get_cached_response(cache_key)
    if cached_weather:
        return jsonify(cached_weather)
    
    # If not in cache, fetch from API
    weather_data = fetch_weather_from_api(city)
    
    # Cache the response for 10 minutes
    cache_api_response(cache_key, weather_data, 600)
    
    return jsonify(weather_data)
```

#### Simple In-Memory Caching:
```python
from datetime import datetime, timedelta
import threading

class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                data, expiry = self.cache[key]
                if datetime.now() < expiry:
                    return data
                else:
                    del self.cache[key]
            return None
    
    def set(self, key, data, seconds=600):
        with self.lock:
            expiry = datetime.now() + timedelta(seconds=seconds)
            self.cache[key] = (data, expiry)

# Global cache instance
cache = SimpleCache()
```

### Error Handling and Fallbacks

```python
def robust_api_call(url, fallback_data=None):
    """Make API call with error handling and fallbacks"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.warning(f"API timeout for {url}")
        return fallback_data
    except requests.exceptions.RequestException as e:
        logger.error(f"API error for {url}: {e}")
        return fallback_data

@app.route('/api/weather/<city>')
def get_weather_robust(city):
    # Try to get from cache first
    cache_key = f"weather:{city}"
    cached_weather = get_cached_response(cache_key)
    if cached_weather:
        return jsonify(cached_weather)
    
    # Fallback weather data
    fallback_weather = {
        'temperature': 22,
        'description': 'Weather data temporarily unavailable',
        'humidity': 50,
        'windSpeed': 5
    }
    
    # Make API call with fallback
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    weather_data = robust_api_call(url, fallback_weather)
    
    # Cache successful responses
    if weather_data != fallback_weather:
        cache_api_response(cache_key, weather_data, 600)
    
    return jsonify(weather_data)
```

This comprehensive guide provides everything you need to integrate free APIs and social login functionality into your Marrakech travel website. All the APIs mentioned have generous free tiers that should be sufficient for a travel website, and the implementation examples show best practices for security, caching, and error handling.

