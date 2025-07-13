import requests
import time
import json

def test_flask_app_with_progress():
    print("🔧 TESTING FLASK APP 4K DOWNLOAD WITH PROGRESS TRACKING")
    print("=" * 60)
    
    url = "https://www.youtube.com/watch?v=G7KNmW9a75Y"
    
    # 1. Check quality detection
    print("1️⃣ Testing quality detection...")
    try:
        response = requests.post('http://127.0.0.1:5000/video-info', 
                               json={'url': url}, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available qualities: {data.get('available_qualities', [])}")
            
            if '4K' in str(data.get('available_qualities', [])):
                print("🌟 4K detected!")
            else:
                print("❌ 4K not detected")
                return
        else:
            print(f"❌ Quality check failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Quality check error: {e}")
        return
    
    # 2. Start download
    print("\n2️⃣ Starting 4K download...")
    try:
        response = requests.post('http://127.0.0.1:5000/download', 
                               json={'url': url, 'quality': '4K'}, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            download_id = result.get('download_id')
            print(f"✅ Download started with ID: {download_id}")
            
            if not download_id:
                print("❌ No download ID returned")
                return
        else:
            print(f"❌ Download start failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Download start error: {e}")
        return
    
    # 3. Monitor progress
    print("\n3️⃣ Monitoring download progress...")
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f'http://127.0.0.1:5000/progress/{download_id}', 
                                  timeout=10)
            
            if response.status_code == 200:
                progress = response.json()
                status = progress.get('status', 'unknown')
                
                if status == 'finished':
                    filename = progress.get('filename', 'Unknown')
                    print(f"🎉 DOWNLOAD COMPLETED! File: {filename}")
                    return
                elif status == 'error':
                    error = progress.get('error', 'Unknown error')
                    print(f"❌ Download failed: {error}")
                    return
                elif status == 'downloading':
                    percent = progress.get('percent', '0%')
                    speed = progress.get('speed', 'N/A')
                    eta = progress.get('eta', 'N/A')
                    print(f"📥 Downloading... {percent} | Speed: {speed} | ETA: {eta}")
                else:
                    print(f"⏳ Status: {status}")
            else:
                print(f"❌ Progress check failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Progress check error: {e}")
        
        time.sleep(5)  # Check every 5 seconds
    
    print("⏰ Download timeout reached")

if __name__ == "__main__":
    test_flask_app_with_progress()
