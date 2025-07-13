import yt_dlp
import json

def deep_format_analysis():
    print("🔍 DEEP FORMAT ANALYSIS - MILEY CYRUS FLOWERS")
    print("=" * 70)
    
    url = "https://www.youtube.com/watch?v=G7KNmW9a75Y"
    
    print(f"🎯 Analyzing: {url}")
    print("📊 Extracting ALL available formats...")
    
    # Configure yt-dlp for maximum format detection
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'listformats': True,  # List all formats
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web', 'ios', 'mweb'],  # All possible clients
                'player_skip': ['configs'],
            }
        },
        'cookiefile': 'cookies.txt',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("🎬 Extracting comprehensive video info...")
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'N/A')
            print(f"\n✅ Title: {title}")
            print(f"📺 Duration: {info.get('duration', 0)} seconds")
            print(f"👤 Uploader: {info.get('uploader', 'N/A')}")
            
            formats = info.get('formats', [])
            print(f"\n🎞️ TOTAL FORMATS FOUND: {len(formats)}")
            
            # Separate video and audio formats
            video_formats = []
            audio_formats = []
            combined_formats = []
            
            for f in formats:
                format_id = f.get('format_id', 'N/A')
                ext = f.get('ext', 'N/A')
                height = f.get('height')
                width = f.get('width')
                vcodec = f.get('vcodec', 'N/A')
                acodec = f.get('acodec', 'N/A')
                filesize = f.get('filesize')
                tbr = f.get('tbr', 'N/A')
                
                format_note = f.get('format_note', '')
                quality = f.get('quality', 'N/A')
                
                if height and vcodec != 'none':
                    if acodec != 'none':
                        combined_formats.append({
                            'id': format_id, 'height': height, 'width': width,
                            'vcodec': vcodec, 'acodec': acodec, 'ext': ext,
                            'filesize': filesize, 'tbr': tbr, 'note': format_note
                        })
                    else:
                        video_formats.append({
                            'id': format_id, 'height': height, 'width': width,
                            'vcodec': vcodec, 'ext': ext,
                            'filesize': filesize, 'tbr': tbr, 'note': format_note
                        })
                elif acodec != 'none':
                    audio_formats.append({
                        'id': format_id, 'acodec': acodec, 'ext': ext,
                        'filesize': filesize, 'tbr': tbr, 'note': format_note
                    })
            
            # Sort by height (highest first)
            video_formats.sort(key=lambda x: x['height'], reverse=True)
            combined_formats.sort(key=lambda x: x['height'], reverse=True)
            
            print(f"\n🎬 VIDEO-ONLY FORMATS ({len(video_formats)} found):")
            for i, vf in enumerate(video_formats[:15]):  # Show top 15
                size_info = f"{vf['filesize']/(1024*1024):.1f}MB" if vf['filesize'] else "N/A"
                print(f"   {i+1:2d}. ID:{vf['id']:>6} | {vf['width']}x{vf['height']} | {vf['vcodec']:>12} | {vf['ext']} | {size_info:>8} | {vf['note']}")
            
            print(f"\n🎥 COMBINED FORMATS ({len(combined_formats)} found):")
            for i, cf in enumerate(combined_formats[:10]):  # Show top 10
                size_info = f"{cf['filesize']/(1024*1024):.1f}MB" if cf['filesize'] else "N/A"
                print(f"   {i+1:2d}. ID:{cf['id']:>6} | {cf['width']}x{cf['height']} | V:{cf['vcodec']:>8} A:{cf['acodec']:>8} | {size_info:>8}")
            
            # Check for 4K specifically
            ultra_hd = [f for f in video_formats + combined_formats if f['height'] >= 2160]
            quad_hd = [f for f in video_formats + combined_formats if 1440 <= f['height'] < 2160]
            full_hd = [f for f in video_formats + combined_formats if 1080 <= f['height'] < 1440]
            
            print(f"\n🎯 HIGH QUALITY ANALYSIS:")
            print(f"   4K Formats (2160p+): {len(ultra_hd)}")
            print(f"   1440p Formats: {len(quad_hd)}")
            print(f"   1080p Formats: {len(full_hd)}")
            
            if ultra_hd:
                print(f"\n🌟 4K FORMATS DETECTED!")
                for uhd in ultra_hd[:3]:
                    size_info = f"{uhd['filesize']/(1024*1024):.1f}MB" if uhd['filesize'] else "Unknown"
                    print(f"   🎬 {uhd['width']}x{uhd['height']} | {uhd['vcodec']} | {size_info}")
                print(f"\n❓ WHY ISN'T 4K BEING DETECTED IN OUR API?")
                print(f"   This suggests our format filtering needs adjustment!")
            else:
                print(f"\n❌ NO 4K FORMATS FOUND")
                print(f"   The highest quality available might be limited")
            
            # Test what 'best' format would actually select
            print(f"\n🔍 TESTING 'BEST' FORMAT SELECTION:")
            test_opts = ydl_opts.copy()
            test_opts['format'] = 'best'
            test_opts['simulate'] = True
            
            try:
                with yt_dlp.YoutubeDL(test_opts) as test_ydl:
                    test_info = test_ydl.extract_info(url, download=False)
                    selected_format = test_info.get('format_id', 'N/A')
                    selected_height = test_info.get('height', 'N/A')
                    selected_width = test_info.get('width', 'N/A')
                    print(f"   Selected format ID: {selected_format}")
                    print(f"   Selected resolution: {selected_width}x{selected_height}")
            except Exception as e:
                print(f"   ❌ Format selection test failed: {e}")
                
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    deep_format_analysis()
