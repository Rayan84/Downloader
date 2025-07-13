import yt_dlp
import time

def test_fallback_download():
    """Test download with fallback strategies for blocked videos"""
    print("🔄 TESTING FALLBACK DOWNLOAD STRATEGIES")
    print("=" * 60)
    
    # Test URL - use a simple, known working video
    test_urls = [
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo - usually works
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - popular test
    ]
    
    for url in test_urls:
        print(f"\n🎯 Testing URL: {url}")
        
        # Strategy 1: Android client with minimal options
        print("📱 Strategy 1: Android client (simple)")
        try:
            ydl_opts = {
                'outtmpl': 'downloads/test_android_%(title)s.%(ext)s',
                'format': 'best[height<=720]/best',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                    }
                },
                'quiet': False,
                'no_warnings': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("✅ Android strategy SUCCESS!")
            break
            
        except Exception as e:
            print(f"❌ Android strategy failed: {e}")
        
        # Strategy 2: Web client with cookies
        print("🌐 Strategy 2: Web client with cookies")
        try:
            ydl_opts = {
                'outtmpl': 'downloads/test_web_%(title)s.%(ext)s',
                'format': 'best[height<=480]/worst',
                'cookiefile': 'cookies.txt',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                },
                'quiet': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("✅ Web strategy SUCCESS!")
            break
            
        except Exception as e:
            print(f"❌ Web strategy failed: {e}")
        
        # Strategy 3: iOS client
        print("📱 Strategy 3: iOS client")
        try:
            ydl_opts = {
                'outtmpl': 'downloads/test_ios_%(title)s.%(ext)s',
                'format': 'worst/best[height<=360]',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                    }
                },
                'quiet': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("✅ iOS strategy SUCCESS!")
            break
            
        except Exception as e:
            print(f"❌ iOS strategy failed: {e}")
        
        print(f"❌ All strategies failed for {url}")
        time.sleep(2)  # Wait between URLs

if __name__ == "__main__":
    test_fallback_download()
