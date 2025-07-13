import requests
import time

def test_enhanced_flask():
    print("🧪 TESTING ENHANCED FLASK APP WITH FALLBACK STRATEGIES")
    print("=" * 65)
    
    base_url = "http://127.0.0.1:5000"
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # Me at the zoo
    
    # 1. Test video info
    print("1️⃣ Testing video info...")
    try:
        response = requests.post(f'{base_url}/video-info', 
                               json={'url': test_url}, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Title: {data.get('title', 'Unknown')}")
            print(f"✅ Available qualities: {data.get('available_qualities', [])}")
        else:
            print(f"❌ Video info failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Video info error: {e}")
        return
    
    # 2. Test download with worst quality (most likely to work)
    print("\n2️⃣ Testing download with 'worst' quality...")
    try:
        response = requests.post(f'{base_url}/download', 
                               json={'url': test_url, 'quality': 'worst'}, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            download_id = result.get('download_id')
            print(f"✅ Download started: {download_id}")
            
            # Monitor progress
            print("\n3️⃣ Monitoring progress...")
            timeout = 120  # 2 minutes
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(f'{base_url}/progress/{download_id}', 
                                          timeout=10)
                    
                    if response.status_code == 200:
                        progress = response.json()
                        status = progress.get('status', 'unknown')
                        
                        if status == 'finished':
                            filename = progress.get('filename', 'Unknown')
                            print(f"🎉 DOWNLOAD SUCCESS! File: {filename}")
                            return
                        elif status == 'error':
                            error = progress.get('error', 'Unknown error')
                            print(f"❌ Download failed: {error}")
                            return
                        elif status == 'downloading':
                            percent = progress.get('percent', '0%')
                            speed = progress.get('speed', 'N/A')
                            print(f"📥 Downloading... {percent} | Speed: {speed}")
                        else:
                            print(f"⏳ Status: {status}")
                    
                except Exception as e:
                    print(f"❌ Progress check error: {e}")
                
                time.sleep(3)
            
            print("⏰ Download timeout reached")
            
        else:
            print(f"❌ Download start failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Download error: {e}")

if __name__ == "__main__":
    test_enhanced_flask()
