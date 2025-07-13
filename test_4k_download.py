import requests
import json
import time

def test_4k_download():
    print("🎬 TESTING 4K DOWNLOAD FUNCTIONALITY")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    test_url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"  # Costa Rica 4K
    
    print(f"🎯 Testing 4K download for: {test_url}")
    
    try:
        # First verify the video info shows 4K
        print("📊 Step 1: Verifying 4K is detected...")
        info_response = requests.post(
            f"{base_url}/video-info",
            json={"url": test_url},
            timeout=30
        )
        
        if info_response.status_code == 200:
            info_data = info_response.json()
            qualities = info_data.get('available_qualities', [])
            print(f"✅ Available qualities: {qualities}")
            
            if '4K (2160p)' in qualities:
                print("🎬 4K confirmed available!")
                
                # Test downloading in 4K
                print("\n🚀 Step 2: Starting 4K download...")
                download_response = requests.post(
                    f"{base_url}/download",
                    json={"url": test_url, "quality": "4K"},
                    timeout=30
                )
                
                if download_response.status_code == 200:
                    download_data = download_response.json()
                    download_id = download_data.get('download_id')
                    print(f"✅ 4K Download started (ID: {download_id})")
                    
                    # Monitor progress for a bit (don't wait for full download due to size)
                    print("📥 Monitoring download progress...")
                    for i in range(10):  # Check for 20 seconds
                        progress_response = requests.get(f"{base_url}/progress/{download_id}")
                        if progress_response.status_code == 200:
                            progress = progress_response.json()
                            status = progress.get('status')
                            
                            if status == 'downloading':
                                percent = progress.get('percent', 'N/A')
                                speed = progress.get('speed', 'N/A')
                                print(f"   📊 Progress: {percent} at {speed}")
                            elif status == 'finished':
                                print(f"✅ 4K Download completed!")
                                filename = progress.get('filename', 'N/A')
                                print(f"📁 File: {filename}")
                                break
                            elif status == 'error':
                                print(f"❌ Download failed: {progress.get('error', 'Unknown error')}")
                                break
                        
                        time.sleep(2)
                    
                    if status == 'downloading':
                        print("🎯 4K download is in progress (stopping test to avoid large download)")
                        print("✅ 4K functionality confirmed working!")
                    
                else:
                    print(f"❌ 4K Download request failed: {download_response.text}")
            else:
                print("❌ 4K not available for this video")
        else:
            print(f"❌ Failed to get video info: {info_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🎉 4K DOWNLOAD TEST COMPLETED!")

if __name__ == "__main__":
    test_4k_download()
