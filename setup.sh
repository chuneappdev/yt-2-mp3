#!/bin/bash

# YouTube to MP3/MP4 Downloader Setup Script

echo "🚀 Setting up YouTube Downloader..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install additional dependencies for video processing
echo "🎵 Installing additional media dependencies..."
pip install ffmpeg-python

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed. Some audio conversion features may not work."
    echo "To install FFmpeg:"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Ubuntu: sudo apt install ffmpeg"
    echo "  - Windows: Download from https://ffmpeg.org/download.html"
fi

# Create .env file from example
if [ ! -f .env ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env
    echo "✅ Please edit .env file with your configuration"
fi

# Set up directories
echo "📁 Setting up directories..."
mkdir -p static/downloads
mkdir -p logs

# Create a simple run script
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python app.py
EOF

chmod +x run.sh

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Edit .env file with your configuration"
echo "  2. Run: ./run.sh"
echo "  3. Open http://localhost:5000 in your browser"
echo ""
echo "📋 Next steps:"
echo "  - Update Google Ads configuration in .env"
echo "  - Configure Google Analytics (optional)"
echo "  - Install FFmpeg for audio conversion"
echo ""
