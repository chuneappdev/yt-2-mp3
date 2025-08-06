# 🎵 YouTube to MP3/MP4 Downloader

A beautiful, fast, and responsive YouTube downloader built with modern web technologies. Features a clean MVC architecture, Tailwind CSS styling, and Google Ads integration.

![YouTube Downloader Screenshot](https://via.placeholder.com/800x400/1F2937/FFFFFF?text=YouTube+Downloader)

## ✨ Features

- **🎵 Dual Format Support**: Download as MP3 (audio) or MP4 (video)
- **🚀 Lightning Fast**: Optimized download engine with progress tracking
- **📱 Mobile Responsive**: Beautiful design that works on all devices
- **🎨 Modern UI**: Clean, gradient-based design with smooth animations
- **💰 Monetization Ready**: Google Ads integration for revenue generation
- **🔒 Secure**: Input validation and safe file handling
- **📊 Analytics**: Built-in Google Analytics support
- **🐳 Docker Ready**: Easy deployment with Docker and Docker Compose

## 🏗️ Architecture

### MVC Structure
```
yt_to_mp3/
├── app.py                    # Flask application entry point
├── models/
│   └── downloader.py         # YouTube download logic
├── controllers/
│   └── download_controller.py # Request handling and validation
├── templates/
│   └── index.html           # Main UI template
├── static/
│   ├── css/style.css        # Custom styles and animations
│   ├── js/
│   │   ├── app.js          # Main application logic
│   │   └── ads.js          # Google Ads integration
│   └── downloads/          # Temporary file storage
└── logs/                   # Application logs
```

### Technology Stack
- **Backend**: Python Flask with yt-dlp
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Media Processing**: FFmpeg for audio conversion
- **Deployment**: Docker, Nginx, Gunicorn
- **Monetization**: Google AdSense integration

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
git clone <your-repo-url>
cd yt_to_mp3
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd yt_to_mp3

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required for MP3 conversion)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from https://ffmpeg.org/

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the application
python app.py
```

### Option 3: Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t youtube-downloader .
docker run -p 5000:5000 youtube-downloader
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key

# Google Ads (Replace with your actual IDs)
GOOGLE_ADS_CLIENT_ID=ca-pub-XXXXXXXXXX
GOOGLE_ADS_SLOT_ID=1234567890

# Google Analytics (Optional)
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID

# Download Limits
MAX_FILE_SIZE_MB=100
DOWNLOAD_TIMEOUT_SECONDS=300
MAX_DOWNLOADS_PER_IP_PER_HOUR=10
```

### Google Ads Setup
1. Sign up for [Google AdSense](https://www.google.com/adsense/)
2. Get your publisher ID and ad slot ID
3. Update `.env` file with your IDs
4. Replace placeholder IDs in `static/js/ads.js`

### Google Analytics Setup
1. Create a [Google Analytics](https://analytics.google.com/) account
2. Get your measurement ID
3. Update `.env` file
4. Uncomment analytics initialization in `static/js/ads.js`

## 🎨 Customization

### Styling
- **Colors**: Modify Tailwind config in `templates/index.html`
- **Animations**: Edit CSS in `static/css/style.css`
- **Layout**: Update HTML structure in `templates/index.html`

### Functionality
- **Download Logic**: Modify `models/downloader.py`
- **API Endpoints**: Update `controllers/download_controller.py`
- **Frontend Behavior**: Edit `static/js/app.js`

## 📊 Monetization Features

### Ad Integration
- **Download Completion Ads**: Shows ad modal after successful download
- **Fallback Ads**: Custom promotional content when AdSense fails
- **Ad Blocker Detection**: Friendly message for users with ad blockers
- **Social Sharing**: Alternative monetization through viral sharing

### Revenue Optimization
- **Ad Rotation**: Multiple ad types for better engagement
- **Performance Tracking**: Monitor ad impressions and clicks
- **Rate Limiting**: Prevents abuse while maximizing legitimate use

## 🔧 API Endpoints

### Core Endpoints
```
GET  /                    # Main application page
POST /api/download        # Start download process
GET  /api/progress/{id}   # Check download progress
GET  /api/file/{filename} # Serve completed downloads
POST /api/info           # Get video information
GET  /api/health         # Health check endpoint
```

### API Examples
```javascript
// Start download
fetch('/api/download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        url: 'https://youtube.com/watch?v=...',
        format: 'mp3' // or 'mp4'
    })
});

// Check progress
fetch('/api/progress/download_1234567890');

// Get video info
fetch('/api/info', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        url: 'https://youtube.com/watch?v=...'
    })
});
```

## 🚀 Deployment

### Production Deployment
1. **Update Configuration**:
   ```bash
   # Set production values in .env
   FLASK_ENV=production
   SECRET_KEY=your-secure-production-key
   ```

2. **Use Gunicorn**:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
   ```

3. **Set up Nginx** (optional):
   ```bash
   # Use provided nginx.conf
   sudo cp nginx.conf /etc/nginx/sites-available/youtube-downloader
   sudo ln -s /etc/nginx/sites-available/youtube-downloader /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```

### Cloud Deployment
- **Heroku**: Ready for deployment with included `Procfile`
- **AWS**: Use Docker image with ECS or Elastic Beanstalk
- **Google Cloud**: Deploy with Cloud Run or App Engine
- **DigitalOcean**: Use App Platform or Droplets with Docker

## 🛡️ Security Features

- **Input Validation**: Comprehensive URL and parameter validation
- **Rate Limiting**: Prevents abuse and server overload
- **File Safety**: Secure file handling and cleanup
- **CORS Protection**: Configurable cross-origin request handling
- **Error Handling**: Graceful error responses without information leakage

## 📈 Performance Optimization

- **Async Downloads**: Non-blocking download processing
- **File Cleanup**: Automatic cleanup of old downloads
- **Gzip Compression**: Reduced bandwidth usage
- **CDN Ready**: Static assets optimized for CDN delivery
- **Caching Headers**: Appropriate cache policies for assets

## 🐛 Troubleshooting

### Common Issues

**FFmpeg not found**:
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

**Downloads failing**:
- Check YouTube URL format
- Verify FFmpeg installation
- Check network connectivity
- Review application logs

**Ads not showing**:
- Verify Google AdSense account status
- Check ad blocker detection
- Ensure correct publisher ID

### Debug Mode
```bash
# Enable debug logging
export FLASK_ENV=development
python app.py
```

### Logs
- Application logs: `logs/app.log`
- Download progress: Check browser developer tools
- Server errors: Check terminal output

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- **Documentation**: This README and inline code comments
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and community

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the download engine
- [Tailwind CSS](https://tailwindcss.com/) for the beautiful styling
- [Font Awesome](https://fontawesome.com/) for icons
- [Flask](https://flask.palletsprojects.com/) for the web framework

---

**Built with ❤️ for the YouTube community**
