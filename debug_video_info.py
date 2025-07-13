import requests
import json

def debug_video_info():
    print("🔧 DEBUGGING VIDEO INFO ENDPOINT")
    print("=" * 50)
    
    url = "https://www.youtube.com/watch?v=G7KNmW9a75Y"
    
    try:
        response = requests.post('http://127.0.0.1:5000/video-info', 
                               json={'url': url}, 
                               timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_video_info()
