import requests
import json
import time

# Test the quality improvements
def test_quality_improvements():
    print("🧪 TESTING YOUTUBE DOWNLOADER QUALITY IMPROVEMENTS")
    print("=" * 60)
    
    # Sample YouTube URLs for testing (using well-known, public videos)
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - Classic test video
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo - First YouTube video
    ]
    
    base_url = "http://127.0.0.1:5000"
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🎬 TEST {i}: Testing video quality detection")
        print(f"URL: {url}")
        
        try:
            # Test video info extraction
            print("📊 Getting video information...")
            info_response = requests.post(
                f"{base_url}/video-info",
                json={"url": url},
                timeout=30
            )
            
            if info_response.status_code == 200:
                info_data = info_response.json()
                print(f"✅ Video Info Retrieved:")
                print(f"   Title: {info_data.get('title', 'N/A')}")
                print(f"   Duration: {info_data.get('duration', 0)} seconds")
                print(f"   Available Qualities: {info_data.get('available_qualities', [])}")
                print(f"   Formats Available: {info_data.get('formats_count', 0)}")
                
                # Test download with best quality
                print("\n🚀 Starting download with 'best' quality...")
                download_response = requests.post(
                    f"{base_url}/download",
                    json={"url": url, "quality": "best"},
                    timeout=30
                )
                
                if download_response.status_code == 200:
                    download_data = download_response.json()
                    download_id = download_data.get('download_id')
                    print(f"✅ Download started (ID: {download_id})")
                    
                    # Monitor progress
                    for _ in range(60):  # Wait up to 60 seconds
                        progress_response = requests.get(f"{base_url}/progress/{download_id}")
                        if progress_response.status_code == 200:
                            progress = progress_response.json()
                            status = progress.get('status')
                            
                            if status == 'downloading':
                                print(f"📥 Progress: {progress.get('percent', 'N/A')} - Speed: {progress.get('speed', 'N/A')}")
                            elif status == 'finished':
                                print(f"✅ Download completed: {progress.get('filename', 'N/A')}")
                                break
                            elif status == 'error':
                                print(f"❌ Download failed: {progress.get('error', 'Unknown error')}")
                                break
                        
                        time.sleep(2)
                    
                else:
                    print(f"❌ Download request failed: {download_response.text}")
                    
            else:
                print(f"❌ Video info request failed: {info_response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print(f"\n📊 Running quality analysis of downloaded files...")
    
    # Run the quality analyzer
    try:
        from quality_analyzer import analyze_downloads
        analyze_downloads()
    except Exception as e:
        print(f"❌ Could not run quality analyzer: {e}")
    
    print(f"\n🎉 Quality test completed!")
    print(f"💡 Check the downloads folder to see the results")

if __name__ == "__main__":
    test_quality_improvements()
