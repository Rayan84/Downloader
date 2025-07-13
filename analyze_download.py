import requests
import json

def analyze_url_and_download():
    print("🔍 ANALYZING YOUR DOWNLOAD vs PROVIDED URL")
    print("=" * 70)
    
    # Your updated YouTube URL
    original_url = "https://youtu.be/G7KNmW9a75Y?list=RDMM"
    clean_url = "https://www.youtube.com/watch?v=G7KNmW9a75Y"  # Standard format
    
    print(f"🎯 Original URL: {original_url}")
    print(f"🎯 Clean URL: {clean_url}")
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        print("\n📊 Getting video info from your URL...")
        response = requests.post(
            f"{base_url}/video-info",
            json={"url": clean_url},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Video Title: {data.get('title', 'N/A')}")
            print(f"📺 Duration: {data.get('duration', 0)} seconds")
            print(f"👤 Uploader: {data.get('uploader', 'N/A')}")
            print(f"🎞️ Available Qualities: {data.get('available_qualities', [])}")
            print(f"📊 Total Formats: {data.get('formats_count', 0)}")
            
            # Check if this matches recent downloads
            title = data.get('title', '')
            print(f"\n🔍 CHECKING IF THIS MATCHES RECENT DOWNLOADS:")
            
            import os
            if os.name == 'nt':
                downloads_folder = os.path.join(os.environ['USERPROFILE'], 'Downloads')
            else:
                downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
            recent_files = os.listdir(downloads_folder)

            print("📁 Recent downloads:")
            for file in sorted(recent_files, key=lambda x: os.path.getmtime(os.path.join(downloads_folder, x)), reverse=True)[:5]:
                if file.endswith('.mp4'):
                    size = os.path.getsize(os.path.join(downloads_folder, file))
                    size_mb = size / (1024 * 1024)
                    print(f"   • {file} ({size_mb:.1f} MB)")
            
            # Check for 4K availability
            qualities = data.get('available_qualities', [])
            has_4k = any('4K' in q or '2160p' in q for q in qualities)
            has_1440p = any('1440p' in q for q in qualities)
            
            print(f"\n🎬 QUALITY ANALYSIS:")
            if has_4k:
                print("✅ 4K AVAILABLE! This video supports 4K download")
            elif has_1440p:
                print("✅ 1440p AVAILABLE! This video supports high quality download")
            else:
                max_quality = max([q for q in qualities if any(x in q for x in ['1080p', '720p', '480p', '360p', '240p'])], 
                                default='Unknown')
                print(f"📺 MAXIMUM QUALITY: {max_quality}")
            
            # Provide download recommendation
            print(f"\n💡 DOWNLOAD RECOMMENDATIONS:")
            if has_4k:
                print("   🎬 Use '4K (2160p)' or 'Best Available' for maximum quality")
                print("   📊 Expected file size: 50-200+ MB depending on duration")
            elif has_1440p:
                print("   🎥 Use '1440p' or 'Best Available' for high quality")  
                print("   📊 Expected file size: 20-100 MB depending on duration")
            else:
                print("   🟣 Use 'Best Available' for highest available quality")
                print("   📊 Expected file size varies by quality")
                
        else:
            print(f"❌ Failed to get video info: {response.text}")
            
    except Exception as e:
        print(f"❌ Error analyzing URL: {e}")

if __name__ == "__main__":
    analyze_url_and_download()
