from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from controllers.download_controller import DownloadController

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS for Railway deployment
allowed_origins = [
    'https://web-production-ccb44.up.railway.app',
    'http://localhost:5000',
    'http://127.0.0.1:5000'
]

# Add any custom origins from environment
cors_origins = os.getenv('CORS_ORIGINS', '')
if cors_origins:
    allowed_origins.extend(cors_origins.split(','))

CORS(app, origins=allowed_origins)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'downloads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE_MB', 100)) * 1024 * 1024

# Ensure required folders exist
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Initialize controller
try:
    download_controller = DownloadController()
    app.logger.info("Download controller initialized successfully")
except Exception as e:
    app.logger.error(f"Failed to initialize download controller: {e}")
    download_controller = None

# Background cleanup setup
import threading
import time

def cleanup_worker():
    """Background worker to clean up old files"""
    while True:
        try:
            # Run cleanup every 6 hours
            cleaned = download_controller.cleanup_old_files(max_age_hours=24)
            if cleaned > 0:
                app.logger.info(f"Cleaned up {cleaned} old files")
        except Exception as e:
            app.logger.error(f"Error in cleanup worker: {e}")
        
        # Sleep for 6 hours
        time.sleep(6 * 3600)

# Start background cleanup worker
cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
cleanup_thread.start()
app.logger.info("Background cleanup worker started")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download():
    """Handle download requests"""
    app.logger.info(f"Download request from {request.remote_addr}")
    return download_controller.download(request)

@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    """Get download progress"""
    return download_controller.get_progress(task_id)

@app.route('/api/file/<filename>')
def download_file(filename):
    """Serve downloaded files"""
    app.logger.info(f"File download request for {filename} from {request.remote_addr}")
    return download_controller.serve_file(filename, app.config['DOWNLOAD_FOLDER'])

@app.route('/api/info', methods=['POST'])
def get_video_info():
    """Get video information"""
    return download_controller.get_video_info(request)

@app.route('/api/test', methods=['GET'])
def test_yt_dlp():
    """Test yt-dlp functionality"""
    try:
        import yt_dlp
        
        # Test with a known working video (shorter video for faster testing)
        test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video
        
        ydl_opts = {
            'quiet': True, 
            'format': 'best/worst',
            'no_warnings': True,
            'ignoreerrors': False,
            'no_check_certificate': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
        return jsonify({
            'success': True,
            'yt_dlp_version': yt_dlp.version.__version__,
            'test_video_title': info.get('title', 'Unknown'),
            'test_video_duration': info.get('duration', 0),
            'message': 'yt-dlp is working correctly'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'yt-dlp test failed - try a different video URL'
        }), 500

@app.route('/api/stats')
def get_stats():
    """Get download statistics"""
    stats = download_controller.get_stats()
    return jsonify(stats)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        status = 'healthy' if download_controller else 'unhealthy'
        return jsonify({
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'controller_ready': download_controller is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    # Railway provides PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.logger.info(f"Starting YouTube Downloader on port {port}")
    app.run(debug=debug, host='0.0.0.0', port=port)
