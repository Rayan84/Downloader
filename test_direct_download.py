import yt_dlp
import os

def test_direct_download():
    print("🔧 TESTING DIRECT DOWNLOAD WITH FFMPEG")
    print("=" * 60)
    
    url = "https://www.youtube.com/watch?v=G7KNmW9a75Y"
    
    # Test direct download with ffmpeg
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'bestvideo[width>=3840]+bestaudio/bestvideo[height>=1080]+bestaudio/best',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android', 'ios'],
                'player_skip': ['configs'],
            }
        },
        'cookiefile': 'cookies.txt',
    }
    
    try:
        print(f"🎯 Downloading: {url}")
        print(f"🎬 Format: {ydl_opts['format']}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print("✅ Download completed!")
        
        # Check the downloaded file
        downloads_folder = "downloads"
        if os.path.exists(downloads_folder):
            files = [f for f in os.listdir(downloads_folder) if f.endswith('.mp4')]
            if files:
                latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(downloads_folder, x)))
                filepath = os.path.join(downloads_folder, latest_file)
                size = os.path.getsize(filepath)
                size_mb = size / (1024 * 1024)
                
                print(f"📁 Downloaded: {latest_file}")
                print(f"📊 File size: {size_mb:.1f} MB")
                
                if size_mb > 50:
                    print("🌟 SUCCESS! High quality download (likely 4K)")
                elif size_mb > 20:
                    print("🟣 GOOD! High quality download (likely 1080p+)")
                elif size_mb > 10:
                    print("🟠 DECENT! Medium quality download")
                else:
                    print("🟡 File size still seems low")
            else:
                print("❌ No video files found in downloads folder")
        else:
            print("❌ Downloads folder not found")
            
    except Exception as e:
        print(f"❌ Download failed: {e}")

if __name__ == "__main__":
    test_direct_download()
