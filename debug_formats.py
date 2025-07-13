import yt_dlp
import json

def debug_youtube_formats():
    print("🔍 DEBUGGING YOUTUBE FORMAT EXTRACTION")
    print("=" * 60)
    
    # Test URL known to have 4K
    test_url = "https://www.youtube.com/watch?v=LXb3EKWsInQ"  # Costa Rica 4K
    
    print(f"Testing URL: {test_url}")
    print("=" * 60)
    
    # Configure yt-dlp with maximum format access
    ydl_opts = {
        'quiet': False,  # Enable output to see what's happening
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web', 'ios'],  # Try multiple clients
                'player_skip': ['configs'],
            }
        },
        'cookiefile': 'cookies.txt',
        'format': 'all',  # List all available formats
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("🎬 Extracting video info...")
            info = ydl.extract_info(test_url, download=False)
            
            print(f"✅ Title: {info.get('title', 'N/A')}")
            print(f"📊 Total formats available: {len(info.get('formats', []))}")
            
            # Analyze all formats
            formats = info.get('formats', [])
            print(f"\n🎞️ DETAILED FORMAT ANALYSIS:")
            print("=" * 80)
            
            video_formats = []
            audio_formats = []
            
            for i, f in enumerate(formats):
                format_id = f.get('format_id', 'N/A')
                ext = f.get('ext', 'N/A')
                height = f.get('height')
                width = f.get('width')
                vcodec = f.get('vcodec', 'N/A')
                acodec = f.get('acodec', 'N/A')
                filesize = f.get('filesize')
                tbr = f.get('tbr', 'N/A')
                
                resolution = f"{width}x{height}" if width and height else "N/A"
                size_mb = f"{filesize / (1024*1024):.1f} MB" if filesize else "N/A"
                
                format_info = {
                    'id': format_id,
                    'ext': ext,
                    'resolution': resolution,
                    'height': height,
                    'vcodec': vcodec,
                    'acodec': acodec,
                    'size': size_mb,
                    'tbr': tbr
                }
                
                if height:  # Video format
                    video_formats.append(format_info)
                elif acodec != 'none':  # Audio format
                    audio_formats.append(format_info)
            
            # Sort video formats by height (highest first)
            video_formats.sort(key=lambda x: x['height'] if x['height'] else 0, reverse=True)
            
            print(f"📺 VIDEO FORMATS ({len(video_formats)} found):")
            for vf in video_formats[:10]:  # Show top 10
                print(f"   ID: {vf['id']:>6} | {vf['resolution']:>10} | {vf['ext']:>4} | {vf['vcodec']:>12} | {vf['size']:>10} | {vf['tbr']} tbr")
            
            # Check for 4K formats
            ultra_hd_formats = [vf for vf in video_formats if vf['height'] and vf['height'] >= 2160]
            quad_hd_formats = [vf for vf in video_formats if vf['height'] and vf['height'] >= 1440]
            full_hd_formats = [vf for vf in video_formats if vf['height'] and vf['height'] >= 1080]
            
            print(f"\n🎯 QUALITY ANALYSIS:")
            print(f"   8K+ formats (4320p+): {len([vf for vf in video_formats if vf['height'] and vf['height'] >= 4320])}")
            print(f"   4K formats (2160p+): {len(ultra_hd_formats)}")
            print(f"   1440p formats: {len([vf for vf in quad_hd_formats if vf['height'] < 2160])}")
            print(f"   1080p formats: {len([vf for vf in full_hd_formats if vf['height'] < 1440])}")
            print(f"   720p formats: {len([vf for vf in video_formats if vf['height'] and 720 <= vf['height'] < 1080])}")
            
            if ultra_hd_formats:
                print(f"\n🌟 4K FORMATS FOUND!")
                for uhd in ultra_hd_formats[:3]:
                    print(f"   🎬 {uhd['resolution']} | {uhd['ext']} | {uhd['vcodec']} | {uhd['size']}")
            else:
                print(f"\n❌ NO 4K FORMATS DETECTED")
                if video_formats:
                    highest = video_formats[0]
                    print(f"   Highest available: {highest['resolution']} ({highest['height']}p)")
            
            # Check if this might be due to region restrictions or authentication
            print(f"\n🔍 TROUBLESHOOTING:")
            if len(formats) < 10:
                print("   ⚠️  Very few formats detected - might be region-locked or require authentication")
            if not ultra_hd_formats and "4K" in info.get('title', ''):
                print("   ⚠️  Video title mentions 4K but no 4K formats found - possible restrictions")
            
            print(f"\n💡 RECOMMENDATIONS:")
            print("   • Try different video URLs known to have public 4K content")
            print("   • Check if the video actually has 4K (not just title)")
            print("   • Some videos restrict high quality to authenticated users")
            print("   • Try using fresh cookies from a logged-in YouTube session")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This might indicate network issues or YouTube blocking the request")

if __name__ == "__main__":
    debug_youtube_formats()
