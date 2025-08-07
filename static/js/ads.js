// Google Ads Integration Manager
class AdManager {
    constructor() {
        this.adDisplayed = false;
        this.adConfig = {
            adSlot: 'ca-app-pub-3940256099942544/6300978111', // Test ad slot - replace with your actual ad slot
            adFormat: 'rectangle',
            adSize: [300, 250]
        };
        this.init();
    }

    init() {
        // Initialize Google AdSense if not already loaded
        if (typeof window.adsbygoogle === 'undefined') {
            this.loadGoogleAds();
        }
    }

    loadGoogleAds() {
        // Create script element for Google AdSense
        const script = document.createElement('script');
        script.async = true;
        script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';
        script.setAttribute('data-ad-client', 'ca-pub-3940256099942544'); // Test publisher ID - replace with your actual publisher ID
        
        // Add error handling
        script.onerror = () => {
            console.log('Failed to load Google Ads - using fallback');
            this.initFallbackAd();
        };
        
        script.onload = () => {
            console.log('Google Ads loaded successfully');
            this.initGoogleAds();
        };

        document.head.appendChild(script);
    }

    initGoogleAds() {
        // Initialize AdSense
        try {
            (adsbygoogle = window.adsbygoogle || []).push({});
        } catch (error) {
            console.log('AdSense initialization error:', error);
            this.initFallbackAd();
        }
    }

    showAd() {
        const adContainer = document.getElementById('googleAd');
        
        if (typeof window.adsbygoogle !== 'undefined' && !this.adDisplayed) {
            this.displayGoogleAd(adContainer);
        } else {
            this.displayFallbackAd(adContainer);
        }
        
        this.adDisplayed = true;
    }

    displayGoogleAd(container) {
        // Clear existing content
        container.innerHTML = '';
        
        // Create ad element
        const adElement = document.createElement('ins');
        adElement.className = 'adsbygoogle';
        adElement.style.display = 'block';
        adElement.setAttribute('data-ad-client', 'ca-pub-XXXXXXXXXX'); // Replace with your publisher ID
        adElement.setAttribute('data-ad-slot', this.adConfig.adSlot);
        adElement.setAttribute('data-ad-format', this.adConfig.adFormat);
        adElement.setAttribute('data-full-width-responsive', 'true');
        
        container.appendChild(adElement);
        
        try {
            (adsbygoogle = window.adsbygoogle || []).push({});
        } catch (error) {
            console.log('Ad display error:', error);
            this.displayFallbackAd(container);
        }
    }

    displayFallbackAd(container) {
        // Create a fallback ad (could be your own promotional content)
        container.innerHTML = `
            <div class="bg-gradient-to-br from-blue-500 to-purple-600 text-white p-6 rounded-lg text-center h-full flex flex-col justify-center">
                <div class="mb-4">
                    <i class="fas fa-star text-3xl text-yellow-300 mb-2"></i>
                    <h3 class="text-xl font-bold mb-2">Love Our Service?</h3>
                    <p class="text-sm opacity-90">Help us keep it free by sharing!</p>
                </div>
                <div class="flex justify-center space-x-4">
                    <button onclick="adManager.shareOnTwitter()" class="bg-blue-400 hover:bg-blue-500 px-4 py-2 rounded-lg transition-colors">
                        <i class="fab fa-twitter"></i> Tweet
                    </button>
                    <button onclick="adManager.shareOnFacebook()" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition-colors">
                        <i class="fab fa-facebook"></i> Share
                    </button>
                </div>
            </div>
        `;
    }

    initFallbackAd() {
        // Set up fallback advertising system
        console.log('Setting up fallback ad system');
    }

    // Social sharing functions
    shareOnTwitter() {
        const text = encodeURIComponent('Just downloaded a YouTube video with this amazing free tool! 🎵');
        const url = encodeURIComponent(window.location.href);
        window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank', 'width=600,height=400');
    }

    shareOnFacebook() {
        const url = encodeURIComponent(window.location.href);
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank', 'width=600,height=400');
    }

    // Analytics tracking
    trackAdView() {
        // Track ad impressions
        if (typeof gtag !== 'undefined') {
            gtag('event', 'ad_impression', {
                'event_category': 'advertising',
                'event_label': 'download_complete'
            });
        }
    }

    trackAdClick() {
        // Track ad clicks
        if (typeof gtag !== 'undefined') {
            gtag('event', 'ad_click', {
                'event_category': 'advertising',
                'event_label': 'download_complete'
            });
        }
    }

    // Revenue optimization
    rotateAds() {
        // Implement ad rotation logic
        const adTypes = ['google', 'fallback', 'promotional'];
        const randomType = adTypes[Math.floor(Math.random() * adTypes.length)];
        return randomType;
    }

    // Ad blocker detection
    detectAdBlocker() {
        return new Promise((resolve) => {
            const testAd = document.createElement('div');
            testAd.innerHTML = '&nbsp;';
            testAd.className = 'adsbox';
            testAd.style.position = 'absolute';
            testAd.style.left = '-9999px';
            document.body.appendChild(testAd);
            
            setTimeout(() => {
                const isBlocked = testAd.offsetHeight === 0;
                document.body.removeChild(testAd);
                resolve(isBlocked);
            }, 100);
        });
    }

    async handleAdBlocker() {
        const isBlocked = await this.detectAdBlocker();
        
        if (isBlocked) {
            // Show message about ad blocker
            this.showAdBlockerMessage();
        }
    }

    showAdBlockerMessage() {
        const container = document.getElementById('googleAd');
        container.innerHTML = `
            <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 p-4 rounded-lg text-center">
                <div class="mb-2">
                    <i class="fas fa-shield-alt text-2xl"></i>
                </div>
                <h3 class="font-bold mb-2">Ad Blocker Detected</h3>
                <p class="text-sm mb-3">We use ads to keep this service free. Please consider disabling your ad blocker.</p>
                <button onclick="location.reload()" class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded transition-colors">
                    Refresh Page
                </button>
            </div>
        `;
    }

    // Performance monitoring
    monitorAdPerformance() {
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.name.includes('googlesyndication')) {
                    console.log('Ad load time:', entry.duration);
                }
            }
        });
        
        observer.observe({ entryTypes: ['resource'] });
    }
}

// Initialize ad manager
window.adManager = new AdManager();

// Initialize Google Analytics (optional)
function initGoogleAnalytics() {
    // Replace 'GA_MEASUREMENT_ID' with your actual Google Analytics ID
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID';
    document.head.appendChild(script);
    
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    gtag('js', new Date());
    gtag('config', 'GA_MEASUREMENT_ID');
    
    // Track download events
    window.gtag = gtag;
}

// Initialize analytics on page load
document.addEventListener('DOMContentLoaded', () => {
    // Uncomment to enable Google Analytics
    // initGoogleAnalytics();
    
    // Monitor ad performance
    window.adManager.monitorAdPerformance();
    
    // Check for ad blocker
    window.adManager.handleAdBlocker();
});

// Export for use in other scripts
window.AdManager = AdManager;
