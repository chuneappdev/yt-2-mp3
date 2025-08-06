# YouTube to MP3/MP4 Downloader

A beautiful, responsive YouTube downloader built with Flask, Tailwind CSS, and modern JavaScript.

## Features

- Download YouTube videos as MP3 or MP4
- Clean, modern UI with Tailwind CSS
- MVC architecture for maintainability
- Progress tracking
- Google Ads integration
- Mobile responsive design

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open http://localhost:5000 in your browser

## Project Structure

```
yt_to_mp3/
├── app.py                 # Main Flask application
├── models/
│   ├── __init__.py
│   └── downloader.py      # Download logic
├── controllers/
│   ├── __init__.py
│   └── download_controller.py  # Request handlers
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   ├── js/
│   │   ├── app.js         # Main JavaScript
│   │   └── ads.js         # Google Ads integration
│   └── downloads/         # Downloaded files
└── templates/
    └── index.html         # Main template
```

## Technologies

- **Backend**: Python Flask
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Download Engine**: yt-dlp
- **Architecture**: MVC Pattern
