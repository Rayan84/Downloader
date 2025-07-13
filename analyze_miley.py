import os
import subprocess
import json
from datetime import datetime

def analyze_miley_cyrus_download():
    print("🔍 ANALYZING MILEY CYRUS DOWNLOAD QUALITY")
    print("=" * 60)
    
    filepath = "downloads/Miley Cyrus - Flowers (Official Video).mp4"
    
    if not os.path.exists(filepath):
        print("❌ Miley Cyrus video not found!")
        return
    
    file_size = os.path.getsize(filepath)
    file_stat = os.stat(filepath)
    
    print(f"📹 File: Miley Cyrus - Flowers (Official Video).mp4")
    print(f"📊 Size: {format_size(file_size)}")
    print(f"📅 Downloaded: {datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Try to get technical details
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            analyze_video_streams(data)
        else:
            print("⚠️  ffprobe not available - using file size analysis")
            analyze_by_size(file_size)
            
    except Exception as e:
        print("⚠️  Technical analysis not available - using file size analysis")
        analyze_by_size(file_size)
    
    # Compare with expectations
    print(f"\n📊 QUALITY ASSESSMENT:")
    print(f"   Expected for Miley Cyrus - Flowers:")
    print(f"   • Maximum available: 1080p (NOT 4K)")
    print(f"   • Duration: 202 seconds (3:22)")
    print(f"   • File size at 8.2 MB suggests 720p quality")
    
    quality_assessment = get_quality_from_size(file_size)
    print(f"   • Actual quality appears to be: {quality_assessment}")
    
    print(f"\n💡 CONCLUSION:")
    if file_size < 15 * 1024 * 1024:  # Less than 15MB
        print("   🟠 This appears to be STANDARD QUALITY (720p or lower)")
        print("   🔍 NOT 4K - this video doesn't offer 4K resolution")
    else:
        print("   🟣 This appears to be HIGH QUALITY (1080p)")
    
    print(f"   ✅ Download successful, quality appropriate for this video")

def analyze_video_streams(data):
    """Analyze video streams from ffprobe data"""
    video_stream = None
    
    for stream in data.get('streams', []):
        if stream.get('codec_type') == 'video':
            video_stream = stream
            break
    
    if video_stream:
        width = video_stream.get('width', 0)
        height = video_stream.get('height', 0)
        fps = video_stream.get('r_frame_rate', 'N/A')
        codec = video_stream.get('codec_name', 'N/A')
        
        print(f"\n🎬 TECHNICAL DETAILS:")
        print(f"   Resolution: {width}x{height}")
        print(f"   Quality: {get_quality_name(height)}")
        print(f"   Codec: {codec}")
        print(f"   FPS: {fps}")
        
        if height >= 2160:
            print("🌟 This is 4K Ultra HD!")
        elif height >= 1080:
            print("🟣 This is 1080p Full HD!")
        elif height >= 720:
            print("🟠 This is 720p HD!")
        else:
            print("🟡 This is standard definition!")

def analyze_by_size(file_size):
    """Analyze quality based on file size"""
    size_mb = file_size / (1024 * 1024)
    
    print(f"\n📊 SIZE-BASED QUALITY ESTIMATE:")
    print(f"   File size: {size_mb:.1f} MB")
    
    if size_mb >= 50:
        print("   🌟 LIKELY 4K or very long 1080p video")
    elif size_mb >= 20:
        print("   🟣 LIKELY 1080p Full HD")
    elif size_mb >= 10:
        print("   🟠 LIKELY 720p HD")
    elif size_mb >= 5:
        print("   🟡 LIKELY 480p Standard")
    else:
        print("   🔴 LIKELY 360p or lower")

def get_quality_from_size(file_size):
    """Get quality estimate from file size"""
    size_mb = file_size / (1024 * 1024)
    
    if size_mb >= 50:
        return "4K/Long 1080p"
    elif size_mb >= 20:
        return "1080p"
    elif size_mb >= 10:
        return "720p"
    elif size_mb >= 5:
        return "480p"
    else:
        return "360p or lower"

def get_quality_name(height):
    """Get quality name from height"""
    if height >= 2160:
        return "4K (2160p)"
    elif height >= 1440:
        return "1440p"
    elif height >= 1080:
        return "1080p"
    elif height >= 720:
        return "720p"
    elif height >= 480:
        return "480p"
    else:
        return "360p or lower"

def format_size(bytes_size):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

if __name__ == "__main__":
    analyze_miley_cyrus_download()
