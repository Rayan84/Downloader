import requests
import time

def test_flask_app():
    print("🔧 TESTING FLASK APP 4K DOWNLOAD")
    print("=" * 50)
    
    # Test URL
    url = "https://www.youtube.com/watch?v=G7KNmW9a75Y"
    
    # First, check if the app detects 4K
    print("1️⃣ Testing quality detection...")
    try:
        response = requests.post('http://127.0.0.1:5000/video-info', 
                               json={'url': url}, 
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available qualities: {data.get('available_qualities', [])}")
            
            if '4K' in str(data.get('available_qualities', [])):
                print("🌟 4K detected! Proceeding with download test...")
            else:
                print("❌ 4K not detected")
                return
        else:
            print(f"❌ Quality check failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Quality check error: {e}")
        return
    
    # Test download
    print("\n2️⃣ Testing 4K download...")
    try:
        response = requests.post('http://127.0.0.1:5000/download', 
                               json={'url': url, 'quality': '4K'}, 
                               timeout=180)  # 3 minutes timeout
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Download response: {result}")
            
            if result.get('status') == 'success':
                print("🎉 FLASK APP 4K DOWNLOAD SUCCESSFUL!")
            else:
                print(f"❌ Download failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ Download request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Download error: {e}")

if __name__ == "__main__":
    test_flask_app()
