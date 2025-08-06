// Main JavaScript for YouTube Downloader
class YouTubeDownloader {
    constructor() {
        this.currentTaskId = null;
        this.progressInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupFormatSelection();
    }

    bindEvents() {
        // URL input events
        const urlInput = document.getElementById('youtubeUrl');
        const pasteBtn = document.getElementById('pasteBtn');
        const downloadBtn = document.getElementById('downloadBtn');

        // Paste button
        pasteBtn.addEventListener('click', async () => {
            try {
                const text = await navigator.clipboard.readText();
                urlInput.value = text;
                this.validateUrl(text);
            } catch (err) {
                console.log('Failed to read clipboard:', err);
            }
        });

        // URL input validation
        urlInput.addEventListener('input', (e) => {
            this.validateUrl(e.target.value);
        });

        urlInput.addEventListener('paste', (e) => {
            setTimeout(() => {
                this.validateUrl(e.target.value);
            }, 100);
        });

        // Download button
        downloadBtn.addEventListener('click', () => {
            this.startDownload();
        });

        // Enter key support
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.startDownload();
            }
        });
    }

    setupFormatSelection() {
        const formatOptions = document.querySelectorAll('.format-option');
        
        formatOptions.forEach(option => {
            option.addEventListener('click', () => {
                // Remove active class from all options
                formatOptions.forEach(opt => opt.classList.remove('active'));
                
                // Add active class to clicked option
                option.classList.add('active');
                
                // Update radio button
                const radio = option.querySelector('input[type="radio"]');
                radio.checked = true;

                // Add visual feedback
                option.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    option.style.transform = '';
                }, 200);
            });
        });
    }

    validateUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=|embed\/|v\/|.+\?v=)?([^&=%\?]{11})/;
        const isValid = youtubeRegex.test(url);
        
        const downloadBtn = document.getElementById('downloadBtn');
        const urlInput = document.getElementById('youtubeUrl');
        
        if (url.length > 0) {
            if (isValid) {
                urlInput.style.borderColor = '#10B981';
                downloadBtn.disabled = false;
                downloadBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                this.getVideoInfo(url);
            } else {
                urlInput.style.borderColor = '#EF4444';
                downloadBtn.disabled = true;
                downloadBtn.classList.add('opacity-50', 'cursor-not-allowed');
                this.hideVideoPreview();
            }
        } else {
            urlInput.style.borderColor = '';
            downloadBtn.disabled = false;
            downloadBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            this.hideVideoPreview();
        }
    }

    async getVideoInfo(url) {
        try {
            const response = await fetch('/api/info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();
            
            if (response.ok && data.success) {
                this.showVideoPreview(data);
            } else {
                console.log('Video info error:', data.error || 'Unknown error');
                this.hideVideoPreview();
            }
        } catch (error) {
            console.log('Failed to get video info:', error);
            this.hideVideoPreview();
        }
    }

    showVideoPreview(videoInfo) {
        const preview = document.getElementById('videoPreview');
        const thumbnail = document.getElementById('videoThumbnail');
        const title = document.getElementById('videoTitle');
        const uploader = document.getElementById('videoUploader');
        const duration = document.getElementById('videoDuration');

        thumbnail.src = videoInfo.thumbnail || '';
        title.textContent = videoInfo.title || 'Unknown Title';
        uploader.textContent = `By: ${videoInfo.uploader || 'Unknown'}`;
        
        if (videoInfo.duration) {
            const minutes = Math.floor(videoInfo.duration / 60);
            const seconds = videoInfo.duration % 60;
            duration.textContent = `Duration: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        }

        preview.classList.remove('hidden');
        preview.classList.add('video-preview-enter');
        
        setTimeout(() => {
            preview.classList.remove('video-preview-enter');
            preview.classList.add('video-preview-enter-active');
        }, 10);
    }

    hideVideoPreview() {
        const preview = document.getElementById('videoPreview');
        preview.classList.add('hidden');
        preview.classList.remove('video-preview-enter-active');
    }

    async startDownload() {
        const url = document.getElementById('youtubeUrl').value.trim();
        const format = document.querySelector('input[name="format"]:checked').value;
        const downloadBtn = document.getElementById('downloadBtn');

        if (!url) {
            this.showError('Please enter a YouTube URL');
            return;
        }

        // Disable button and show loading
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<div class="spinner"></div>Starting Download...';

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url, format: format })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.currentTaskId = data.task_id;
                this.showProgress();
                this.startProgressPolling();
                this.showSuccess('Download started successfully!');
            } else {
                const errorMsg = data.error || 'Download failed';
                this.showError(errorMsg);
                this.resetButton();
            }
        } catch (error) {
            this.showError('Network error: Please check your connection and try again');
            this.resetButton();
        }
    }

    showProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.classList.remove('hidden');
        progressSection.scrollIntoView({ behavior: 'smooth' });
    }

    startProgressPolling() {
        this.progressInterval = setInterval(() => {
            this.checkProgress();
        }, 1000);
    }

    async checkProgress() {
        if (!this.currentTaskId) return;

        try {
            const response = await fetch(`/api/progress/${this.currentTaskId}`);
            const data = await response.json();

            if (data.success) {
                const progress = data.progress;
                this.updateProgress(progress);

                if (progress.status === 'finished') {
                    this.onDownloadComplete(progress.filename);
                } else if (progress.status === 'error') {
                    this.onDownloadError(progress.error);
                }
            }
        } catch (error) {
            console.error('Failed to check progress:', error);
        }
    }

    updateProgress(progress) {
        const progressBar = document.getElementById('progressBar');
        const progressPercent = document.getElementById('progressPercent');
        const progressStatus = document.getElementById('progressStatus');

        const percent = Math.round(progress.progress || 0);
        progressBar.style.width = `${percent}%`;
        progressPercent.textContent = `${percent}%`;

        // Update status text
        let statusText = 'Processing...';
        switch (progress.status) {
            case 'starting':
                statusText = 'Initializing download...';
                break;
            case 'downloading':
                statusText = 'Downloading...';
                progressBar.classList.add('progress-active');
                break;
            case 'finished':
                statusText = 'Download completed!';
                progressBar.classList.remove('progress-active');
                break;
            case 'error':
                statusText = 'Download failed!';
                progressBar.classList.remove('progress-active');
                break;
        }
        progressStatus.textContent = statusText;
    }

    onDownloadComplete(filename) {
        clearInterval(this.progressInterval);
        
        // Show download link
        const downloadLink = document.getElementById('downloadLink');
        const fileLink = document.getElementById('fileDownloadLink');
        
        fileLink.href = `/api/file/${filename}`;
        fileLink.download = filename;
        downloadLink.classList.remove('hidden');

        // Show ad before allowing download
        this.showAd(() => {
            fileLink.click();
        });

        this.resetButton();
        this.showSuccess('Download completed successfully!');
    }

    onDownloadError(error) {
        clearInterval(this.progressInterval);
        this.showError(`Download failed: ${error}`);
        this.resetButton();
    }

    showAd(onAdClosed) {
        const adContainer = document.getElementById('adContainer');
        const closeAdBtn = document.getElementById('closeAdBtn');
        
        adContainer.classList.remove('hidden');
        adContainer.classList.add('ad-fade-in');
        
        // Initialize Google Ad (placeholder)
        window.adManager.showAd();
        
        closeAdBtn.onclick = () => {
            adContainer.classList.add('ad-fade-out');
            setTimeout(() => {
                adContainer.classList.add('hidden');
                adContainer.classList.remove('ad-fade-in', 'ad-fade-out');
                onAdClosed();
            }, 500);
        };
    }

    resetButton() {
        const downloadBtn = document.getElementById('downloadBtn');
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = '<i class="fas fa-download mr-3"></i>Download Now';
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg text-white font-semibold max-w-sm ${
            type === 'success' ? 'bg-green-600' : 'bg-red-600'
        }`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} mr-2"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        // Add entrance animation
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);

        // Add shake animation for errors
        if (type === 'error') {
            const urlInput = document.getElementById('youtubeUrl');
            urlInput.classList.add('error-shake');
            setTimeout(() => {
                urlInput.classList.remove('error-shake');
            }, 500);
        }
    }
}

// Initialize the downloader when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.downloader = new YouTubeDownloader();
});

// Add some visual enhancements
document.addEventListener('DOMContentLoaded', () => {
    // Add floating animation to feature icons
    const featureIcons = document.querySelectorAll('.w-16.h-16');
    featureIcons.forEach((icon, index) => {
        setTimeout(() => {
            icon.classList.add('float-animation');
        }, index * 200);
    });

    // Add glow effect to main title
    const title = document.querySelector('h1');
    if (title) {
        setInterval(() => {
            title.classList.toggle('glow');
        }, 3000);
    }
});
