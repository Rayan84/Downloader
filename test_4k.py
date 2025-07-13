import requests
import json

def test_4k_support():
    print("🎬 TESTING 4K SUPPORT IN YOUTUBE DOWNLOADER")
    print("=" * 60)
    
    # Test with videos known to have 4K quality
    test_urls = [
        "https://www.youtube.com/watch?v=LXb3EKWsInQ",  # Costa Rica 4K Nature video (common 4K test)
        "https://www.youtube.com/watch?v=aqz-KE-bpKQ",  # Big Buck Bunny 4K
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll for comparison
    ]
    
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 Testing video info extraction for 4K detection...")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📺 TEST {i}: {url}")
        
        try:
            # Test video info extraction
            response = requests.post(
                f"{base_url}/video-info",
                json={"url": url},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Title: {data.get('title', 'N/A')}")
                print(f"📊 Available Qualities: {data.get('available_qualities', [])}")
                print(f"🎞️ Total Formats: {data.get('formats_count', 0)}")
                
                # Check if 4K or higher qualities are detected
                qualities = data.get('available_qualities', [])
                has_4k = any('4K' in q or '2160p' in q for q in qualities)
                has_8k = any('8K' in q or '4320p' in q for q in qualities)
                has_1440p = any('1440p' in q for q in qualities)
                
                if has_8k:
                    print("🌟 8K DETECTED! This video supports ultra-high resolution")
                elif has_4k:
                    print("🎬 4K DETECTED! This video supports 4K resolution")
                elif has_1440p:
                    print("🎥 1440p DETECTED! This video supports Quad HD")
                else:
                    print("📺 Standard qualities only (up to 1080p)")
                    
            else:
                print(f"❌ Failed to get video info: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 4K SUPPORT TEST COMPLETED!")
    print(f"💡 If 4K was detected, you can now download in 4K quality!")
    print(f"🚀 Try downloading with 'Best Available' or '4K' quality option")

if __name__ == "__main__":
    test_4k_support()
