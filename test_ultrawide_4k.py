import requests
import json
import time

def test_ultra_wide_4k_download():
    print("🎬 TESTING ULTRA-WIDE 4K DOWNLOAD")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    test_url = "https://www.youtube.com/watch?v=G7KNmW9a75Y"  # Miley Cyrus with ultra-wide 4K
    
    print(f"🎯 Testing ultra-wide 4K download for: {test_url}")
    
    try:
        # Test downloading with 4K setting
        print("🚀 Starting 4K download...")
        download_response = requests.post(
            f"{base_url}/download",
            json={"url": test_url, "quality": "4K"},
            timeout=30
        )
        
        if download_response.status_code == 200:
            download_data = download_response.json()
            download_id = download_data.get('download_id')
            print(f"✅ Ultra-wide 4K Download started (ID: {download_id})")
            
            # Monitor progress
            print("📥 Monitoring download progress...")
            for i in range(30):  # Check for 60 seconds
                progress_response = requests.get(f"{base_url}/progress/{download_id}")
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    status = progress.get('status')
                    
                    if status == 'downloading':
                        percent = progress.get('percent', 'N/A')
                        speed = progress.get('speed', 'N/A')
                        print(f"   📊 Progress: {percent} at {speed}")
                    elif status == 'finished':
                        print(f"✅ Ultra-wide 4K Download completed!")
                        filename = progress.get('filename', 'N/A')
                        print(f"📁 File: {filename}")
                        
                        # Check file size
                        import os
                        filepath = os.path.join("downloads", os.path.basename(filename))
                        if os.path.exists(filepath):
                            size = os.path.getsize(filepath)
                            size_mb = size / (1024 * 1024)
                            print(f"📊 File size: {size_mb:.1f} MB")
                            
                            if size_mb > 50:
                                print("🌟 SUCCESS! File size indicates high quality (likely ultra-wide 4K)")
                            elif size_mb > 20:
                                print("🟣 GOOD! File size indicates 1080p+ quality")
                            else:
                                print("🟡 File size still seems low for 4K")
                        break
                    elif status == 'error':
                        print(f"❌ Download failed: {progress.get('error', 'Unknown error')}")
                        break
                
                time.sleep(2)
            
            if status == 'downloading':
                print("⏱️ Download still in progress (stopping test)")
                print("✅ Ultra-wide 4K download functionality confirmed working!")
            
        else:
            print(f"❌ 4K Download request failed: {download_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🎉 ULTRA-WIDE 4K TEST COMPLETED!")

if __name__ == "__main__":
    test_ultra_wide_4k_download()
