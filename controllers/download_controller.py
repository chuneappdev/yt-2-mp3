from flask import jsonify, send_file
import os
import re
import time
import json
from models.downloader import YouTubeDownloader

class DownloadController:
    """Controller for handling download requests"""
    
    def __init__(self):
        self.downloader = YouTubeDownloader()
        self.downloads_meta_file = os.path.join(os.getcwd(), 'static', 'downloads', '.downloads_meta.json')
        self._ensure_meta_file()
    
    def _ensure_meta_file(self):
        """Ensure the downloads metadata file exists"""
        try:
            downloads_dir = os.path.dirname(self.downloads_meta_file)
            os.makedirs(downloads_dir, exist_ok=True)
            
            if not os.path.exists(self.downloads_meta_file):
                self._save_meta({})
        except Exception as e:
            print(f"Error creating meta file: {e}")
    
    def _load_meta(self):
        """Load downloads metadata"""
        try:
            if os.path.exists(self.downloads_meta_file):
                with open(self.downloads_meta_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading meta: {e}")
            return {}
    
    def _save_meta(self, meta):
        """Save downloads metadata"""
        try:
            with open(self.downloads_meta_file, 'w') as f:
                json.dump(meta, f, indent=2)
        except Exception as e:
            print(f"Error saving meta: {e}")
    
    def _register_download(self, filename, task_id):
        """Register a completed download"""
        meta = self._load_meta()
        meta[filename] = {
            'task_id': task_id,
            'created_at': time.time(),
            'downloaded': False,
            'download_count': 0
        }
        self._save_meta(meta)
    
    def validate_youtube_url(self, url):
        """Validate if the URL is a valid YouTube URL"""
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/',
            r'(https?://)?(www\.)?youtube\.com/watch\?v=',
            r'(https?://)?(www\.)?youtu\.be/',
            r'(https?://)?(www\.)?youtube\.com/embed/',
        ]
        
        for pattern in youtube_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def download(self, request):
        """Handle download request"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            url = data.get('url', '').strip()
            format_type = data.get('format', 'mp3').lower()
            
            # Validation
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            
            if not self.validate_youtube_url(url):
                return jsonify({
                    'success': False,
                    'error': 'Please provide a valid YouTube URL'
                }), 400
            
            if format_type not in ['mp3', 'mp4']:
                return jsonify({
                    'success': False,
                    'error': 'Format must be mp3 or mp4'
                }), 400
            
            # Get video info first
            video_info = self.downloader.get_video_info(url)
            if not video_info['success']:
                return jsonify({
                    'success': False,
                    'error': f'Failed to get video info: {video_info["error"]}'
                }), 400
            
            # Start download
            download_path = os.path.join(os.getcwd(), 'static', 'downloads')
            task_id = self.downloader.start_download(url, format_type, download_path)
            
            return jsonify({
                'success': True,
                'task_id': task_id,
                'video_info': video_info,
                'message': f'Download started for {format_type.upper()} format'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Server error: {str(e)}'
            }), 500
    
    def get_progress(self, task_id):
        """Get download progress"""
        try:
            progress = self.downloader.get_progress(task_id)
            
            # If download is finished and has a filename, register it
            if (progress.get('status') == 'finished' and 
                progress.get('filename') and 
                progress.get('filename') not in self._load_meta()):
                
                self._register_download(progress['filename'], task_id)
            
            return jsonify({
                'success': True,
                'progress': progress
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def serve_file(self, filename, download_folder):
        """Serve downloaded file"""
        try:
            file_path = os.path.join(download_folder, filename)
            
            if not os.path.exists(file_path):
                # Log the missing file for debugging
                print(f"File not found: {file_path}")
                print(f"Available files: {os.listdir(download_folder) if os.path.exists(download_folder) else 'Directory not found'}")
                
                return jsonify({
                    'success': False,
                    'error': 'File not found'
                }), 404
            
            # Ensure file is readable
            if not os.access(file_path, os.R_OK):
                return jsonify({
                    'success': False,
                    'error': 'File not accessible'
                }), 403
            
            # Update download metadata
            meta = self._load_meta()
            if filename in meta:
                meta[filename]['downloaded'] = True
                meta[filename]['download_count'] += 1
                meta[filename]['last_download'] = time.time()
                self._save_meta(meta)
            
            # Get file size for logging
            file_size = os.path.getsize(file_path)
            print(f"Serving file: {filename} ({file_size} bytes)")
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename
            )
            
        except Exception as e:
            print(f"Error serving file {filename}: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_video_info(self, request):
        """Get video information without downloading"""
        try:
            data = request.get_json()
            url = data.get('url', '').strip()
            
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            
            if not self.validate_youtube_url(url):
                return jsonify({
                    'success': False,
                    'error': 'Please provide a valid YouTube URL'
                }), 400
            
            video_info = self.downloader.get_video_info(url)
            return jsonify(video_info)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def cleanup_old_files(self, max_age_hours=24):
        """Clean up old downloaded files"""
        try:
            download_folder = os.path.join(os.getcwd(), 'static', 'downloads')
            meta = self._load_meta()
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            files_to_remove = []
            
            # Check each file in metadata
            for filename, file_meta in meta.items():
                file_path = os.path.join(download_folder, filename)
                
                # Skip if file doesn't exist anymore
                if not os.path.exists(file_path):
                    files_to_remove.append(filename)
                    continue
                
                # Remove files older than max_age that have been downloaded
                file_age = current_time - file_meta.get('created_at', 0)
                has_been_downloaded = file_meta.get('downloaded', False)
                
                if file_age > max_age_seconds and has_been_downloaded:
                    try:
                        os.remove(file_path)
                        files_to_remove.append(filename)
                        print(f"Cleaned up old file: {filename}")
                    except Exception as e:
                        print(f"Error removing file {filename}: {e}")
            
            # Remove from metadata
            for filename in files_to_remove:
                meta.pop(filename, None)
            
            # Save updated metadata
            if files_to_remove:
                self._save_meta(meta)
            
            return len(files_to_remove)
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return 0
    
    def get_stats(self):
        """Get download statistics"""
        try:
            meta = self._load_meta()
            download_folder = os.path.join(os.getcwd(), 'static', 'downloads')
            
            total_files = len(meta)
            downloaded_files = sum(1 for m in meta.values() if m.get('downloaded', False))
            total_downloads = sum(m.get('download_count', 0) for m in meta.values())
            
            # Check actual files on disk
            actual_files = [f for f in os.listdir(download_folder) 
                          if not f.startswith('.') and os.path.isfile(os.path.join(download_folder, f))]
            
            return {
                'total_files': total_files,
                'downloaded_files': downloaded_files,
                'total_downloads': total_downloads,
                'files_on_disk': len(actual_files),
                'disk_files': actual_files
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
