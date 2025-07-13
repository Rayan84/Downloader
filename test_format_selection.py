import yt_dlp
import os

def test_format_selection():
    print("🔍 TESTING FORMAT SELECTION FOR ULTRA-WIDE 4K")
    print("=" * 60)
    
    url = "https://www.youtube.com/watch?v=G7KNmW9a75Y"
    
    # Test different format selection strings
    test_formats = [
        'best[width>=3840]',
        'best[height>=1400]',
        'bestvideo[width>=3840]+bestaudio/best',
        'bestvideo[ext=mp4][width>=3840]+bestaudio[ext=m4a]/best',
        '625+234/best',  # Specific ultra-wide 4K format + audio
        '625',  # Just the ultra-wide 4K format
    ]
    
    ydl_opts_base = {
        'quiet': True,
        'simulate': True,  # Don't actually download
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
    
    for i, format_str in enumerate(test_formats, 1):
        print(f"\n🧪 TEST {i}: Format string '{format_str}'")
        
        ydl_opts = ydl_opts_base.copy()
        ydl_opts['format'] = format_str
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                selected_format_id = info.get('format_id', 'N/A')
                width = info.get('width', 'N/A')
                height = info.get('height', 'N/A')
                filesize = info.get('filesize')
                
                size_info = f"{filesize/(1024*1024):.1f}MB" if filesize else "Unknown size"
                
                print(f"   Selected: Format {selected_format_id} | {width}x{height} | {size_info}")
                
                if width >= 3840:
                    print(f"   🌟 SUCCESS! This would download ultra-wide 4K!")
                elif width >= 1920:
                    print(f"   🟣 This would download 1080p+ quality")
                else:
                    print(f"   🟡 This would download lower quality")
                    
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print(f"\n💡 RECOMMENDATION:")
    print(f"   The format that works best should be used in the app.py")

if __name__ == "__main__":
    test_format_selection()
