import yt_dlp
import os
import threading
import time
from datetime import datetime

class YouTubeDownloader:
    """Model for handling YouTube downloads"""
    
    def __init__(self):
        self.progress_data = {}
        self.download_threads = {}
    
    def get_video_info(self, url):
        """Get video information with enhanced format detection and geo-bypass"""
        try:
            error_msg = "Failed to get video information"
            
            # Multiple configurations with different strategies
            ydl_configs = [
                # Config 1: Standard with basic geo-bypass
                {
                    'quiet': True,
                    'no_warnings': True,
                    'extractaudio': False,
                    'noplaylist': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'geo_bypass': True,
                    'geo_bypass_country': 'US',
                    'format': 'best/bestvideo+bestaudio/worst',  # More flexible format selection
                    'ignoreerrors': True,
                    'extract_flat': False,
                },
                # Config 2: Mobile user agent with Canada bypass
                {
                    'quiet': True,
                    'no_warnings': True,
                    'extractaudio': False,
                    'noplaylist': True,
                    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                    'geo_bypass': True,
                    'geo_bypass_country': 'CA',
                    'format': 'worst/best',  # Try worst quality first to ensure availability
                    'ignoreerrors': True,
                },
                # Config 3: Most permissive with multiple bypasses
                {
                    'quiet': True,
                    'no_warnings': True,
                    'extractaudio': False,
                    'noplaylist': True,
                    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                    'geo_bypass': True,
                    'geo_bypass_country': 'GB',
                    'format': 'mp4/worst',  # Try basic mp4 format
                    'ignoreerrors': True,
                    'extractor_args': {'youtube': {'skip': ['dash']}},  # Skip DASH formats which can be problematic
                },
                # Config 4: Ultra-basic extraction
                {
                    'quiet': True,
                    'no_warnings': True,
                    'extractaudio': False,
                    'noplaylist': True,
                    'format': '18/worst',  # Format 18 is basic 360p mp4, widely available
                    'ignoreerrors': True,
                    'youtube_include_dash_manifest': False,
                }
            ]
            
            last_error = None
            
            for i, ydl_opts in enumerate(ydl_configs):
                try:
                    print(f"Trying config {i+1}/4: {ydl_opts.get('geo_bypass_country', 'no-bypass')}")
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        if info is None:
                            print(f"Config {i+1}: No info returned")
                            continue
                        
                        # Check if we have any formats available
                        formats = info.get('formats', [])
                        if not formats and i < 3:  # Don't fail on last attempt
                            print(f"Config {i+1}: No formats available, trying next")
                            continue
                        
                        print(f"✅ Success with config {i+1}")
                        return {
                            'success': True,
                            'title': info.get('title', 'Unknown'),
                            'duration': info.get('duration', 0),
                            'thumbnail': info.get('thumbnail', ''),
                            'uploader': info.get('uploader', 'Unknown'),
                            'view_count': info.get('view_count', 0),
                            'available_formats': len(formats)
                        }
                except Exception as e:
                    last_error = str(e)
                    print(f"❌ Config {i+1} failed: {last_error}")
                    continue
            
            # If all configs failed
            error_msg = last_error or "All extraction methods failed"
            
        except Exception as e:
            error_msg = str(e)
            
        # Process error message
        print(f"Final yt-dlp error: {error_msg}")
        
        if "No video formats found" in error_msg or "Requested format is not available" in error_msg:
            error_msg = "This video format is not available. Try a different video or check if it's age-restricted."
        elif "Video unavailable" in error_msg:
            error_msg = "This video is unavailable or has been removed."
        elif "Private video" in error_msg:
            error_msg = "This is a private video and cannot be downloaded."
        elif "This live event" in error_msg:
            error_msg = "Live streams cannot be downloaded. Please try again after the stream ends."
        elif "Sign in to confirm your age" in error_msg:
            error_msg = "This video is age-restricted. Try a different video."
        elif "blocked" in error_msg.lower() or "region" in error_msg.lower():
            error_msg = "This video is blocked in the server's region. Try a popular music video or educational content."
        else:
            error_msg = f"Unable to access video: {error_msg}"
            
        return {
            'success': False,
            'error': error_msg
        }
    
    def download_video(self, url, format_type, download_path, task_id):
        """Download video in specified format"""
        try:
            self.progress_data[task_id] = {
                'status': 'starting',
                'progress': 0,
                'filename': None,
                'error': None,
                'format': format_type,
                'download_path': download_path
            }
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        percent = float(d.get('_percent_str', '0%').replace('%', ''))
                        self.progress_data[task_id]['progress'] = percent
                        self.progress_data[task_id]['status'] = 'downloading'
                    except:
                        pass
                elif d['status'] == 'finished':
                    self.progress_data[task_id]['status'] = 'processing'
                    self.progress_data[task_id]['progress'] = 95
                    
                    # Store the base filename for later
                    filename = os.path.basename(d['filename'])
                    filename_without_ext = os.path.splitext(filename)[0]
                    self.progress_data[task_id]['base_filename'] = filename_without_ext
            
            def postprocessor_hook(d):
                if d['status'] == 'finished':
                    # Final processing complete
                    self.progress_data[task_id]['status'] = 'completed'
                    self.progress_data[task_id]['progress'] = 100
                    
                    # Find the actual file that was created
                    self._find_final_filename(task_id)
            
            # Configure download options based on format with fallback strategies
            if format_type == 'mp3':
                ydl_opts = {
                    'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/worst',  # More permissive audio selection
                    'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'progress_hooks': [progress_hook],
                    'postprocessor_hooks': [postprocessor_hook],
                    'noplaylist': True,
                    'extractaudio': True,
                    'audioformat': 'mp3',
                    'audioquality': '192',
                    'ignoreerrors': True,  # Don't fail completely on minor errors
                    'no_warnings': False,
                    'geo_bypass': True,
                    'geo_bypass_country': 'US',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'youtube_include_dash_manifest': False,  # Skip DASH for compatibility
                    'extractor_args': {'youtube': {'skip': ['dash']}},
                }
            else:  # mp4
                ydl_opts = {
                    'format': 'best[height<=720][ext=mp4]/best[height<=480][ext=mp4]/worst[ext=mp4]/18/worst',  # More fallbacks including format 18
                    'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'postprocessor_hooks': [postprocessor_hook],
                    'noplaylist': True,
                    'merge_output_format': 'mp4',
                    'ignoreerrors': True,  # Don't fail completely on minor errors
                    'no_warnings': False,
                    'geo_bypass': True,
                    'geo_bypass_country': 'US',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'youtube_include_dash_manifest': False,  # Skip DASH for compatibility
                    'extractor_args': {'youtube': {'skip': ['dash']}},
                }
            
            # Try download with primary configuration
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                print(f"Primary download failed: {str(e)}")
                # Try fallback with most basic configuration
                self.progress_data[task_id]['status'] = 'retrying'
                
                if format_type == 'mp3':
                    fallback_opts = {
                        'format': 'worst',  # Use worst quality for reliability
                        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '128',  # Lower quality for reliability
                        }],
                        'progress_hooks': [progress_hook],
                        'postprocessor_hooks': [postprocessor_hook],
                        'noplaylist': True,
                        'extractaudio': True,
                        'ignoreerrors': True,
                        'geo_bypass': True,
                        'youtube_include_dash_manifest': False,
                    }
                else:  # mp4
                    fallback_opts = {
                        'format': '18/worst',  # Format 18 is basic 360p mp4
                        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                        'progress_hooks': [progress_hook],
                        'postprocessor_hooks': [postprocessor_hook],
                        'noplaylist': True,
                        'ignoreerrors': True,
                        'geo_bypass': True,
                        'youtube_include_dash_manifest': False,
                    }
                
                print("Trying fallback download configuration...")
                with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                    ydl.download([url])
                
        except Exception as e:
            self.progress_data[task_id]['status'] = 'error'
            self.progress_data[task_id]['error'] = str(e)
    
    def _find_final_filename(self, task_id):
        """Find the actual filename that was created"""
        try:
            progress = self.progress_data[task_id]
            download_path = progress.get('download_path', '')
            base_filename = progress.get('base_filename', '')
            format_type = progress.get('format', 'mp3')
            
            if not base_filename or not download_path:
                return
            
            # Look for files with the base filename
            for filename in os.listdir(download_path):
                if filename.startswith(base_filename):
                    # Check if it matches our expected format
                    if format_type == 'mp3' and filename.endswith('.mp3'):
                        self.progress_data[task_id]['filename'] = filename
                        self.progress_data[task_id]['status'] = 'finished'
                        return
                    elif format_type == 'mp4' and filename.endswith('.mp4'):
                        self.progress_data[task_id]['filename'] = filename
                        self.progress_data[task_id]['status'] = 'finished'
                        return
            
            # Fallback: look for any file with base filename
            for filename in os.listdir(download_path):
                if base_filename in filename:
                    self.progress_data[task_id]['filename'] = filename
                    self.progress_data[task_id]['status'] = 'finished'
                    return
                    
        except Exception as e:
            print(f"Error finding final filename: {e}")
            self.progress_data[task_id]['status'] = 'error'
            self.progress_data[task_id]['error'] = 'Could not locate final file'
    
    def start_download(self, url, format_type, download_path):
        """Start download in a separate thread"""
        task_id = f"download_{int(time.time())}"
        
        thread = threading.Thread(
            target=self.download_video,
            args=(url, format_type, download_path, task_id)
        )
        thread.daemon = True
        thread.start()
        
        self.download_threads[task_id] = thread
        return task_id
    
    def get_progress(self, task_id):
        """Get download progress for a task"""
        return self.progress_data.get(task_id, {
            'status': 'not_found',
            'progress': 0,
            'filename': None,
            'error': 'Task not found'
        })
    
    def cleanup_old_progress(self, max_age_hours=24):
        """Clean up old progress data"""
        current_time = time.time()
        to_remove = []
        
        for task_id in self.progress_data:
            # Extract timestamp from task_id
            try:
                task_time = int(task_id.split('_')[1])
                if current_time - task_time > max_age_hours * 3600:
                    to_remove.append(task_id)
            except:
                continue
        
        for task_id in to_remove:
            del self.progress_data[task_id]
            if task_id in self.download_threads:
                del self.download_threads[task_id]
